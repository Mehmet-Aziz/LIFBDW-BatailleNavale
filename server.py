#!/usr/bin/env python3

#########################################
#  Etudiants : ne pas modifier ce fichier
#########################################

import sys
from http.server import BaseHTTPRequestHandler, HTTPServer, SimpleHTTPRequestHandler
from logzero import logger
from urllib.parse import urlparse, parse_qs
from os import path
import tomllib
from time import sleep
import psycopg
from jinja2 import Environment, FileSystemLoader, PackageLoader, select_autoescape, TemplateNotFound, TemplateSyntaxError, TemplateError, UndefinedError
import traceback
import mimetypes
import argparse
import pathlib
from shutil import rmtree

# module global variables (directly used by views and templates)
SESSION = dict()  # session content is persistent between request
REQUEST_VARS = dict()  # request variables are not persistent (only for the current request)
GET = dict()
POST = dict()


class WebHandler(BaseHTTPRequestHandler):

    _routes = dict()  # class variable for storing routes

    def _set_response(self, response_code=200, mime_type='text/html; charset=utf-8'):
        """
        Prepare a HTTP response for a request.
        response_code: HTTP status code - https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
        mime_type: type du contenu de la réponse
        """
        self.send_response(response_code)
        self.send_header('Content-type', mime_type)
        self.end_headers()

    def redirect(self, new_url, mime_type='text/html; charset=utf-8'):
        """
        Prepare a HTTP response with redirect to another URL.
        new_url : the destination URL
        mime_type: type du contenu de la réponse
        """
        self.send_response(303)  # code SEE_OTHER
        self.send_header('Location', new_url, mime_type=mime_type)
        self.end_headers()

    def match_route(self, url_path):
        """
        When URL matches a route (fully or first component only), calls the associated controller and template files
        url_path: (part of) URL which matches a route
        Returns: a string contaaining the rendering of the template for the given route 
        """
        global SESSION, REQUEST_VARS, GET, POST
        controleur_file = WebHandler._routes[url_path][0]  # get controller filename corresponding to url_path
        template_name = WebHandler._routes[url_path][1]  # get template filename corresponding to url_path
        with open(controleur_file) as infile:  # execute controller file
            try:
                exec(infile.read())  # security issues, but we assume that the script is run locally only
            except Exception as e:  # print controller error and exit
                traceback.print_exc()
                logger.error(f"Erreur ({controleur_file}) : {e}")
                sys.exit(1)
        try:  # load template filepath from template filename
            template_file = self.server.env.get_template(template_name)
        except (TemplateNotFound, UndefinedError, TemplateError) as e:  # print template error and exit
            logger.error(f"Template non trouvé ({e.message})")
            sys.exit(2)
        except TemplateSyntaxError as e:  # print template syntax error and exit
            logger.error(f"Erreur de syntaxe ({e.filename}, ligne {e.lineno}) : {e.message}")
            sys.exit(3)
        return template_file.render(SESSION=SESSION, REQUEST_VARS=REQUEST_VARS, GET=GET, POST=POST)  # execute template file

    def match_url(self):
        """
        Process an URL for building a response: direct file, path fully matching a route, first component matching a route, or 404 error
        """
        url_path = self.path[1:]  #  remove leading slash
        url_components = url_path.split('/')
        if path.isfile(url_path):  # file on the filesystem (image, css, etc.)
            rawfile = open(url_path, 'rb').read()
            mimetype = mimetypes.MimeTypes().guess_type(url_path)[0]
            self._set_response(mime_type=mimetype)
            self.wfile.write(rawfile)
        elif url_path in WebHandler._routes:  # load a route (full match)
            html_content = self.match_route(url_path)
            self._set_response()
            self.wfile.write(html_content.encode('utf-8'))
        elif len(url_components) > 0 and url_components[0] in WebHandler._routes:  # load a route (first component matching)
            global REQUEST_VARS
            REQUEST_VARS['url_components'] = url_components  # components may be used by controllers and views
            html_content = self.match_route(url_components[0])
            self._set_response()
            self.wfile.write(html_content.encode('utf-8'))
        else:  # error 404
            logger.error(f"Error 404: unable to retrieve file {url_path}")
            SimpleHTTPRequestHandler.send_error(self, 404, "Aucune route/fichier ne correspond à l'URL demandée.")

    def reinit_global_variables(self):
        """
        Reinitialization of variables REQUEST_VARS, GET and POST
        """
        global REQUEST_VARS, GET, POST
        REQUEST_VARS = dict()
        GET = dict()
        POST = dict()

    def do_GET(self):
        """
        Process a GET request by splitting URL for removing query parameters
        """
        self.reinit_global_variables()
        global GET
        url_parts = urlparse('http://' + self.client_address[0] + self.path)
        self.path = url_parts[2]  # keep only path without parameters
        GET = parse_qs(url_parts.query)  # store parameters in GET
        logger.debug(url_parts)
        self.match_url()

    def do_POST(self):
        """
        Process a POST request by retrieving posted data
        """
        self.reinit_global_variables()
        global POST
        content_length = int(self.headers['Content-Length']) # size of POST data
        post_data = self.rfile.read(content_length).decode('utf-8') # POST data
        url_parts = urlparse('http://' + self.client_address[0] + self.path + '?' + post_data)
        logger.debug(url_parts)
        POST = parse_qs(url_parts.query)
        self.match_url()


class WebServer(HTTPServer):

    def __init__(self, address, handler, directory, **kwargs):
        """
        Initialize the web server: check exposed directory, load routes file, load database config file, load init file
        """
        global SESSION
        SESSION = dict()
        # check directory to serve
        self.directory = directory
        if self.directory is None or not path.isdir(self.directory):
            logger.error(f"Directory {self.directory} does not exist (or is not readable).")
            sys.exit(1)
        SESSION['DIRECTORY'] = directory
        sys.path.append(self.directory)  # served directory is added to path for searching packages
        # check routing
        self.routes_file = kwargs.get('routes_file')
        routes = self.extract_routes_from_file(self.routes_file)  # load routes
        handler._routes = routes
        # check and load database config file
        self.config_file = kwargs.get('config_file')  # database config
        config = self.load_toml(self.config_file)
        self.connect_database(config)  # connect to PostgreSQL using config
        # check and execute init_file
        self.init_file = kwargs.get('init_file')
        check_init = self.check_exists_file(self.init_file)
        if check_init:  # execute init file
            with open(self.init_file) as infile:
                exec(infile.read())  # security issues, but we assume that the script is run locally only
        # setup jinja templates
        self.env = Environment(  # class variable for template environment (based on Jinja)
            loader=FileSystemLoader([kwargs.get('templates_dir', self.directory), self.directory + '/templates', ]),
            autoescape=select_autoescape()
        )
        self.env.globals['url_for'] = self.url_for  # function that can be called within template
        super().__init__(address, handler)

    def url_for(self, static_file):
        """
        Build the correct path for static files in templates by updating the path according to DIRECTORY (e.g., 'static/img/abc.jpg' -> '../mon_site/static/img/abc.jpg')
        static_file : filepath (from inside DIRECTORY) to a static file
        Returns: updated filepath including DIRECTORY
        """
        return path.join(SESSION['DIRECTORY'], static_file)

    def load_toml(self, file_path):
        """
        Load a TOML file
        file_path: file path of a TOML file
        Returns: a dictionary object containing information of the TOML file
        """
        with open(file_path, "rb") as f:
            try:
                config = tomllib.load(f)
                return config
            except tomllib.TOMLDecodeError as e:
                logger.error(f"Erreur dans le fichier {file_path} : {e}")
                sys.exit(3)

    def check_exists_file(self, filepath):
        """
        Check that a file exists
        file_path: file path of a file
        Returns: a boolean
        """
        if filepath and path.isfile(filepath):
            logger.info(f"Chargement du fichier {filepath} : ok")
            return True
        else:
            logger.warning(f"Le fichier {filepath} n'existe pas (ou non-readable).")
        return False

    def extract_routes_from_file(self, routes_file):
        """
        Read the routes file (list of dicts) and check/transform the routes as a dict of tuples
        routes_file: file path for routes
        Returns: a dictionary object containing routes as {url1: (controleur1, template1), url2: (controleur2, template2), ...}
        """
        output_routes = dict()
        check_file = self.check_exists_file(routes_file)
        if not check_file:  # if no route file, exit
            sys.exit(1)
        routes = self.load_toml(routes_file)
        for r in routes['routes']:
            url = r['url']
            controleur = r['controleur']
            template = r['template']
            controleur_filepath = path.join(self.directory, controleur)
            template_filepath = path.join(self.directory, template)
            if not path.isfile(controleur_filepath):
                logger.warning(f"Le fichier {controleur_filepath} (pour la route {url}) n'existe pas !")
            else:
                output_routes[url] = (controleur_filepath, template)
        logger.info(f"Fichier {routes_file} : {len(output_routes)} routes trouvées")
        return output_routes

    def get_connexion(self, host, username, password, db, schema, port):
        """
        Connect to the database using provided parameters
        host: database server
        username, password: user and password for authentification on the database server
        db: name of the database to connect to
        schema: database schema to use
        port: database port on which the server listens
        Returns: a database connection object (link), or None
        """
        try:
            connexion = psycopg.connect(host=host, user=username, password=password, dbname=db, port=port, autocommit=True)
            cursor = psycopg.ClientCursor(connexion)  # client-side cursor (because of the SET query)
            cursor.execute("SET search_path TO %s", [schema])  # set path to database schema
        except Exception as e:
            print(e)
            return None
        return connexion

    def connect_database(self, config):
        """
        Manage the connection to the database: extract values from config, manage connection error or success
        config: a dict containing connection information to a database
        Returns: True (or exit with code 2 on error)
        """
        global SESSION
        connexion = self.get_connexion(config['POSTGRESQL_SERVER'], config['POSTGRESQL_USER'], config['POSTGRESQL_PASSWORD'], config['POSTGRESQL_DATABASE'], config.get('POSTGRESQL_SCHEMA', 'public'), config.get('POSTGRESQL_PORT', 5432))
        if connexion is None:
            logger.error("Erreur de connexion au SGBD. Vérifiez les paramètres saisis dans le fichier de configuration toml.")
            sys.exit(2)
        else:
            logger.info("Connexion au SGBD PostgreSQL : ok")
            SESSION["SERVER"] = config['POSTGRESQL_SERVER']
            SESSION["DATABASE"] = config['POSTGRESQL_DATABASE']
            SESSION["USER"] = config['POSTGRESQL_USER']
            SESSION["SCHEMA"] = config.get('POSTGRESQL_SCHEMA', 'public')
            SESSION["DB_PORT"] = config.get('POSTGRESQL_PORT', 5432)
            SESSION["CONNEXION"] = connexion
        return True


#########################################################
# main: process script arguments, and run/reboot server
#########################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', help='website directory that the server will serve')
    parser.add_argument('-c', '--config', default="config-bd.toml", help='filepath of the required database configuration TOML file (default config-bd.toml)')
    parser.add_argument('-i', '--init', default=argparse.SUPPRESS, help='filepath of an optional init python file, executed once at startup (default <directory>/init.py)')
    parser.add_argument('-p', '--port', default=4242, type=int, help='port on which web server listens')
    parser.add_argument('-r', '--routes', default=argparse.SUPPRESS, help='filepath of the required routes TOML file (default <directory>/routes.tml)')
    parser.add_argument('-t', '--templates', default=argparse.SUPPRESS, help='filepath of an additional templates directory')
    args = parser.parse_args()
    if 'routes' not in args:  # if no route file, default value set to <directory>/routes.toml
        args.routes = path.join(args.directory, 'routes.toml')
    if 'init' not in args:  # if no init file, default value set to <directory>/init.py
        args.init = path.join(args.directory, 'init.py')
    if 'templates' not in args:  # if no template directory, default value set to <directory>/templates/
        args.templates = path.join(args.directory, 'templates')

    server_address = ('', args.port)
    while True:
        try:
            httpd = WebServer(server_address, WebHandler, directory=args.directory, routes_file=args.routes, config_file= args.config, init_file=args.init, templates_dir=args.templates)
            logger.info(f"Démarrage du serveur httpd pour exposer {args.directory}...")
            logger.info(f"Redémarrez ou quitter le serveur avec Ctrl-C. Mais vous devez arrêter puis relancer le serveur si vous modifiez un fichier du modèle, le fichier de routes ou celui d'initialisation.")
            logger.info(f"Allez sur http://localhost:{args.port}/")
            httpd.serve_forever()
        except KeyboardInterrupt:
            try:
                logger.info("Redémarrage du serveur dans 2 secondes...")
                logger.info("Appuyer sur Ctrl-C à nouveau pour quitter.")
                sleep(1)
                # suppression du cache (répertoires __pycache__, notamment dans le modèle) avant redémarrage
                # pas suffisant: ex, fichiers modèle aussi chargés en mémoire (import par controleurs) 
                for p in pathlib.Path(args.directory).rglob('__pycache__'):
                    logger.info(f"Suppression du répertoire de cache {p}")
                    rmtree(p, True)
                httpd.server_close()
            except KeyboardInterrupt:  # exit
                break
    logger.info('Arrêt du server httpd.')
    httpd.server_close()


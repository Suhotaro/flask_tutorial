import os

from flask import Flask
from logging.config import dictConfig
from flask import signals


def create_app(test_config=None):
    # create and configure the app

    dictConfig({
        'version': 1,
        'formatters': {'default': {
            # is changeable
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.errorhandler(404)
    def handle(e):
        return f"HOOK ERROR: {e}", 404

    @app.errorhandler(ZeroDivisionError)
    def handle(e):
        return f"zero dibison: ---->> {e} <<----", 500

# signals -------------------------------------------------------------
    def log_template_renders(sender, template, context, **extra):
        sender.logger.debug('Rendering template "%s" with context %s',
                         template.name or 'string template',
                         context)

    from flask import template_rendered
    template_rendered.connect(log_template_renders, app, weak=False)


    def log_request(sender, **extra):
        sender.logger.info('Request context is set up')

    from flask import request_started
    request_started.connect(log_request, app, weak=False)


    def log_response(sender, response, **extra):
        sender.logger.info('Request context is about to close down.  '
                            'Response: %s', response)

    from flask import request_finished
    request_finished.connect(log_response, app, weak=False)

# signals -------------------------------------------------------------

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule('/', endpoint='index')


    app.logger.info(f"signal: {signals.signals_available}")

    app.logger.info("FLASKR IS INITIALIZED")

    return app

# Copyright (c) Meta Platforms, Inc. and affiliates.

import os
import flask
import flask_migrate
import flask_sqlalchemy

from .blueprints import hashing, matching, curation

database = flask_sqlalchemy.SQLAlchemy()
migrate = flask_migrate.Migrate()


def create_app():
    """
    Create and configure the Flask app
    """
    app = flask.Flask(__name__)
    app.config.from_envvar("OMM_CONFIG")
    app.config.update(
        SQLALCHEMY_DATABASE_URI=app.config.get("DATABASE_URI"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )
    database.init_app(app)
    migrate.init_app(app, database)

    @app.route("/")
    def index():
        """
        Sanity check endpoint showing a basic status page
        TODO: in development mode, this could show some useful additional info
        """
        return flask.render_template(
            "index.html.j2", production=app.config.get("PRODUCTION")
        )

    @app.route("/status")
    def status():
        """
        Liveness/readiness check endpoint for your favourite Layer 7 load balancer
        """
        return "I-AM-ALIVE\n"

    # Register Flask blueprints for whichever server roles are enabled...
    # URL prefixing facilitates easy Layer 7 routing :)
    if app.config.get("ROLE_HASHER", False):
        app.register_blueprint(hashing.bp, url_prefix="/h")

    if app.config.get("ROLE_MATCHER", False):
        app.register_blueprint(matching.bp, url_prefix="/m")

    if app.config.get("ROLE_MATCHER", False):
        app.register_blueprint(curation.bp, url_prefix="/c")

    from . import models

    @app.cli.command("seed")
    def seed_data():
        # TODO: This is a placeholder for where some useful seed data can be loaded;
        # particularly important for development
        bank = models.Bank(name="bad_stuff", enabled=True)
        database.session.add(bank)
        database.session.commit()

    return app

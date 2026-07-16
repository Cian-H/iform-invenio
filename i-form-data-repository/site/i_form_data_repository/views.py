"""Additional views."""

from flask import Blueprint

#
# Registration
#
def create_blueprint(app):
    """Register blueprint routes on app."""
    blueprint = Blueprint(
        "i_form_data_repository",
        __name__,
        template_folder="./templates",
    )

    # Add URL rules
    return blueprint

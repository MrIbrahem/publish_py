"""Flask extensions initialization.

This module centralizes Flask extensions to prevent circular imports
and enable proper initialization order with the application factory pattern.
"""

from flask_wtf.csrf import CSRFProtect

# Initialize extensions without binding to app
csrf = CSRFProtect()

# Future extensions can be added here:
# db = SQLAlchemy()
# login_manager = LoginManager()
# migrate = Migrate()

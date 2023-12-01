# blue prints are imported
# explicitly instead of using *
from .user import *
from .index import *
from .review import *
from .staff import *
from .admin import *
from .auth import *
from .admin import *

views = [user_views, index_views, review_views, staff_views, auth_views, admin_views]
# blueprints must be added to this list

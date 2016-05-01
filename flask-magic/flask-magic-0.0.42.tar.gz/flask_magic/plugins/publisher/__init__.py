"""
Publisher

Publisher is a content management system (but don't call it a CMS, LMAO!!!)

The admin allows you to create posts, categorize them etc.

The front end is just a barebone template.

It doesn't do user management itself. This is left to Magic User package.
"""
import os
import datetime
import json

from flask import jsonify
from flask_magic import (Magic, set_meta, get_config, redirect, request, url_for,
                         session, abort, flash, flash_data, get_flashed_data,
                         register_package, init_app)
from flask_magic.decorators import (menu, route, template, plugin, login_required,
                               no_login_required, require_user_roles)
from flask_magic.ext import (mail, cache, storage, recaptcha, csrf,
                         user_authenticated, user_not_authenticated)
from flask_magic.exceptions import (ApplicationError, ModelError, UserError)
from flask_magic import utils
from flask_magic.extras import markdown_ext
from flask_login import login_required, current_user

register_package(__package__)

def model(UserModel):
    """
    Post Model
    :param UserModel:
    """

    db = UserModel.db

    class SlugNameMixin(object):
        name = db.Column(db.String(255), index=True)
        slug = db.Column(db.String(255), index=True, unique=True)
        description = db.Column(db.String(255))
        image_url = db.Column(db.Text)

        @classmethod
        def get_by_slug(cls, slug=None, name=None):
            """
            Return a post by slug
            """
            if name and not slug:
                slug = utils.slugify(name)
            return cls.query().filter(cls.slug == slug).first()

        @classmethod
        def new(cls, name, slug=None):
            slug = utils.slugify(name if not slug else slug)
            return cls.create(name=name, slug=slug)

        def rename(self, name, slug=None):
            slug = utils.slugify(name if not slug else slug)
            return self.update(name=name, slug=slug)

    class PublisherType(SlugNameMixin, db.Model):
        """
        Types
        """
        @property
        def total_posts(self):
            return PublisherPost.query().filter(PublisherPost.type_id == self.id).count()

    class PublisherCategory(SlugNameMixin, db.Model):
        """
        Category
        """
        @property
        def total_posts(self):
            return PublisherCategoryMap.query()\
                .filter(PublisherCategoryMap.category_id == self.id)\
                .count()

    class PublisherTag(SlugNameMixin, db.Model):
        """
        Tag
        """
        @property
        def total_posts(self):
            return PublisherTagMap.query()\
                .filter(PublisherTagMap.tag_id == self.id)\
                .count()

    class PublisherTagMap(db.Model):
        """
        PostPostTag
        """
        post_id = db.Column(db.Integer, db.ForeignKey("publisher_post.id", ondelete='CASCADE'))
        tag_id = db.Column(db.Integer, db.ForeignKey(PublisherTag.id, ondelete='CASCADE'))

        @classmethod
        def add(cls, post_id, tag_id):
            c = cls.query().filter(cls.post_id == post_id)\
                .filter(cls.tag_id == tag_id)\
                .first()
            if not c:
                cls.create(post_id=post_id, tag_id=tag_id)

        @classmethod
        def remove(cls, post_id, tag_id):
            c = cls.query().filter(cls.post_id == post_id)\
                .filter(cls.tag_id == tag_id)\
                .first()
            if c:
                c.delete(hard_delete=True)

    class PublisherCategoryMap(db.Model):
        post_id = db.Column(db.Integer, db.ForeignKey("publisher_post.id", ondelete='CASCADE'))
        category_id = db.Column(db.Integer, db.ForeignKey(PublisherCategory.id, ondelete='CASCADE'))

        @classmethod
        def add(cls, post_id, category_id):
            c = cls.query().filter(cls.post_id == post_id)\
                .filter(cls.category_id == category_id)\
                .first()
            if not c:
                cls.create(post_id=post_id, category_id=category_id)

        @classmethod
        def remove(cls, post_id, category_id):
            c = cls.query().filter(cls.post_id == post_id)\
                .filter(cls.category_id == category_id)\
                .first()
            if c:
                c.delete(hard_delete=True)

    class PublisherPost(db.Model):

        user_id = db.Column(db.Integer, db.ForeignKey(UserModel.id))
        type_id = db.Column(db.Integer, db.ForeignKey(PublisherType.id))

        title = db.Column(db.String(255))
        slug = db.Column(db.String(255), index=True)
        content = db.Column(db.Text)
        description = db.Column(db.Text)
        featured_image = db.Column(db.Text)
        featured_embed = db.Column(db.Text)
        featured_media_top = db.Column(db.String(10))
        language = db.Column(db.String(255))
        parent_id = db.Column(db.Integer)  # If the post is derived from another post
        is_child = db.Column(db.Boolean, index=True, default=False)  #
        is_list = db.Column(db.Boolean, index=True, default=False)  # A list is a type of post having sub post
        is_featured = db.Column(db.Boolean, index=True, default=False)  # Feature post are limited
        featured_at = db.Column(db.DateTime)
        is_sticky = db.Column(db.Boolean, index=True, default=False)  # A sticky post usually stay on top, no matter the count
        sticky_at = db.Column(db.DateTime)
        is_published = db.Column(db.Boolean, index=True, default=True)
        published_at = db.Column(db.DateTime)
        published_by = db.Column(db.Integer)
        is_revision = db.Column(db.Boolean, default=False)
        revision_id = db.Column(db.Integer)  # When updating the post, will auto-save

        is_public = db.Column(db.Boolean, index=True, default=False)
        is_draft = db.Column(db.Boolean, index=True, default=False)
        options_data = db.Column(db.Text, default="{}")
        menu_order = db.Column(db.Integer, default=0, index=True)

        author = db.relationship(UserModel, backref="posts")
        type = db.relationship(PublisherType, backref="posts")
        categories = db.relationship(PublisherCategory,
                                     secondary=PublisherCategoryMap.__table__.name)
        tags = db.relationship(PublisherTag,
                                     secondary=PublisherTagMap.__table__.name)

        @classmethod
        def new(cls, title, **kwargs):
            """
            Insert a new post
            """
            published_date = None
            is_revision = False
            is_published = False
            is_draft = False
            is_public = kwargs.get("is_public", True)
            parent_id = kwargs.get("parent_id", None)

            if kwargs.get("is_revision"):
                if not parent_id:
                    raise ModelError("'parent_id' is missing for revision")
                is_revision = True
                is_public = False
            elif kwargs.get("is_draft"):
                is_draft = True
                is_public = False
            elif kwargs.get("is_published"):
                is_published = True
                published_date = datetime.datetime.now()

            slug = None
            if is_published or is_draft:
                slug = cls.create_slug(kwargs.get("slug", title))

            type_id = kwargs.get("type_id")
            if not type_id and kwargs.get("type_slug"):
                type_slug = kwargs.get("type_slug")
                _type = PublisherType.get_by_slug(slug=type_slug)
                if _type:
                    type_id = _type.id

            data = {
                "user_id": kwargs.get("user_id", 0),
                "title": title,
                "slug": slug,
                "content": kwargs.get("content"),
                "description": kwargs.get("description"),
                "is_published": is_published,
                "published_at": published_date,
                "is_draft": is_draft,
                "is_revision": is_revision,
                "is_public": is_public,
                "parent_id": parent_id,
                "type_id": type_id
            }
            return cls.create(**data)

        @classmethod
        def get_published(cls, id=None, slug=None, types=[], categories=[], tags=[]):
            """
            Return published posts.
            If $id or $slug it will return a single post, else all

            :param id: int - the id of a post
            :param slug: string - the slug of a post
            :param types: list - list of types slugs
            :param categories: list - list of categories slug
            :param tags: list - list of tags slugs
            :return:
            """
            q = cls.query().filter(cls.is_published == True)

            # Query only a single post
            if id or slug:
                if id:
                    q = q.filter(cls.id == id)
                elif slug:
                    q = q.filter(cls.slug == slug)
                return q.first()

            # Query lists
            else:
                if types:
                    q = q.join(PublisherType)\
                        .filter(PublisherType.slug.in_(types))
                if categories:
                    q = q.join(PublisherCategoryMap)\
                        .join(PublisherCategory)\
                        .filter(PublisherCategory.slug.in_(categories))
                if tags:
                    q = q.join(PublisherTag)\
                        .filter(PublisherTag.slug.in_(tags))
                return q

        @classmethod
        def create_slug(cls, title):
            slug = None
            slug_counter = 0
            _slug = utils.slugify(title).lower()
            while True:
                slug = _slug
                if slug_counter > 0:
                    slug += str(slug_counter)
                slug_counter += 1
                if not cls.get_by_slug(slug):
                    break
            return slug

        @classmethod
        def get_by_slug(cls, slug):
            """
            Return a post by slug
            """
            return cls.query().filter(cls.slug == slug).first()

        def publish(self, published_date=None, published_by_id=None):
            if self.is_draft:
                data = {
                    "is_draft": False,
                    "is_published": True,
                    "published_at": published_date or datetime.datetime.now()
                }
                if published_by_id:
                    data.update({
                        "published_by": published_by_id
                    })

                self.update(**data)

        def set_slug(self, title):
            slug = utils.slugify(title)
            if title and slug != self.slug:
                slug = self.create_slug(slug)
                self.update(slug=slug)

        def update_categories(self, categories_list):
            """
            Update categories by replacing existing list with new list
            :param categories_list: list. The new list of category
            """
            cats = PublisherCategoryMap.query()\
                    .filter(PublisherCategoryMap.post_id == self.id)
            cats_list = [c.category_id for c in cats]

            del_cats = list(set(cats_list) - set(categories_list))
            new_cats = list(set(categories_list) - set(cats_list))

            for dc in del_cats:
                PublisherCategoryMap.remove(post_id=self.id, category_id=dc)

            for nc in new_cats:
                PublisherCategoryMap.add(post_id=self.id, category_id=nc)

        def update_tags(self, tags_list):
            """
            Update tags by replacing existing list with new list
            :param tags_list: list. The new list of tags
            """
            tags = PublisherTagMap.query()\
                    .filter(PublisherTagMap.post_id == self.id)
            tags_list_ = [c.tag_id for c in tags]

            del_tags = list(set(tags_list_) - set(tags_list))
            new_tags = list(set(tags_list) - set(tags_list_))

            for dc in del_tags:
                PublisherTagMap.remove(post_id=self.id, tag_id=dc)

            for nc in new_tags:
                PublisherTagMap.add(post_id=self.id, tag_id=nc)

        def get_list(self):
            if not self.is_list:
                return None

            return PublisherPost.query()\
                .filter(PublisherPost.is_published == True)\
                .filter(PublisherPost.is_child == True)\
                .filter(PublisherPost.parent_id == self.id)

        def delete_revisions(self):
            """
            Delete all revisions
            """
            try:
                PublisherPost.query()\
                    .filter(PublisherPost.post_id == self.id)\
                    .filter(PublisherPost.is_revision == True)\
                    .delete()
                PublisherPost.db.commit()
            except Exception as ex:
                PublisherPost.db.rollback()

        def set_options(self, key, values):
            options = self.options
            options.update({key: values})
            self.update(options_data=json.dumps(options))

        @property
        def options(self):
            return json.loads(self.options_data) if self.options_data else {}

        @property
        def excerpt(self):
            """
            Return description as excerpt, if empty,
            it will return the first paragraph
            :return: str
            """
            if self.description:
                return self.description
            else:
                return ""

        @property
        def top_image(self):
            """
            Return the top image
            Return the image url if exists, or it will get the first image
            Will get the first image from the markdown
            """
            if self.featured_image:
                return self.featured_image
            elif self.content:
                md_images = markdown_ext.extract_images(self.content)
                return md_images[0] if md_images else None

        @property
        def status(self):
            if self.is_published:
                return "Published"
            elif self.is_draft:
                return "Draft"
            elif self.is_revision:
                return "Revision"
            else:
                return ""

        @property
        def total_revisions(self):
            return PublisherPost.query()\
                .filter(PublisherPost.post_id == self.id)\
                .filter(PublisherPost.is_revision == True)\
                .count()

    class PublisherUploadObject(db.Model):
        parent_id = db.Column(db.Integer, index=True)
        user_id = db.Column(db.Integer, index=True)
        provider = db.Column(db.String(255))
        container = db.Column(db.String(255))
        local_path = db.Column(db.Text)
        name = db.Column(db.Text)
        description = db.Column(db.String(255))
        size = db.Column(db.Integer)
        extension = db.Column(db.String(10), index=True)
        type = db.Column(db.String(25), index=True)
        object_path = db.Column(db.Text)
        object_url = db.Column(db.Text)
        is_private = db.Column(db.Boolean, index=True, default=False)

    return utils.to_struct(Post=PublisherPost,
                           Category=PublisherCategory,
                           Type=PublisherType,
                           CategoryMap=PublisherCategoryMap,
                           Tag=PublisherTag,
                           TagMap=PublisherTagMap,
                           UploadObject=PublisherUploadObject)


def page(view, **kwargs):
    """
    A plugin to attach the the publisher front-end to your views

    It extends your view  read, list content from the CMS

    kwargs:
        - query: {}
        - menu: {}
        - template_dir
        - endpoint
        - slug
        - title
    """

    # Totally required
    PublisherModel = kwargs.get("model")
    Post = PublisherModel.Post

    view_name = view.__name__
    templates_dir = kwargs.get("template_dir", "Magic/Plugin/Publisher/Page")
    template_page = templates_dir + "/%s.html"
    slug = kwargs.get("slug", "slug")
    endpoint = kwargs.get("endpoint", "pages")
    endpoint_path = "/%s/" % endpoint
    endpoint_namespace = view_name + ":" + endpoint + ":" + "%s"
    title = kwargs.get("title", "")
    description = kwargs.get("description", "")

    query = kwargs.get("query", {})
    query.setdefault("types", [])
    query.setdefault("categories", [])
    query.setdefault("tags", [])
    query.setdefault("order_by", "published_at desc")
    query.setdefault("per_page", 20)

    _menu = kwargs.get("menu", {})
    _menu.setdefault("title", "Pages")
    _menu.setdefault("order", 100)
    _menu.setdefault("visible", True)
    _menu.setdefault("extends", view)
    _menu.pop("endpoint", None)

    #  Options for page_single to customize the slug format
    # It will be used to access the proper endpoint and format the
    slug_format = {
        "id": {
            "url": "{id}",
            "accept": ["id"],
            "route": "%s/<int:id>" % endpoint_path,
            "endpoint": "%s:%s" % (view_name, "id")
        },
        "slug": {
            "url": "{slug}",
            "accept": ["slug"],
            "route": "%s/<slug>" % endpoint_path,
            "endpoint": "%s:%s" % (view_name, "slug")
        },
        "id-slug": {
            "url": "{id}/{slug}",
            "accept": ["id", "slug"],
            "route": "%s/<int:id>/<slug>" % endpoint_path,
            "endpoint": "%s:%s" % (view_name, "id-slug")
        },
        "month-slug": {
            "url": "{month}/{slug}",
            "accept": ["month", "slug"],
            "route": '%s/<regex("[0-9]{4}/[0-9]{2}"):month>/<slug>' % endpoint_path,
            "endpoint": "%s:%s" % (view_name, "month-slug")
        },
        "date-slug": {
            "url": "{date}/{slug}",
            "accept": ["date", "slug"],
            "route": '%s/<regex("[0-9]{4}/[0-9]{2}/[0-9]{2}"):date>/<slug>' % endpoint_path,
            "endpoint": "%s:%s" % (view_name, "id")
        }
    }

    class Page(object):

        @classmethod
        def prepare_post(cls, post):
            """
            Prepare the post data,
            """
            url_kwargs = {
                "id": post.id,
                "slug": post.slug,
                "date": post.published_at.strftime("%Y/%m/%d"),
                "month": post.published_at.strftime("%Y/%m")
            }
            # Filter items not in the 'accept'
            url_kwargs = {_: None if _ not in slug_format.get(slug)["accept"]
                                  else __
                                  for _, __ in url_kwargs.items()}

            url = url_for(slug_format.get(slug)["endpoint"],
                          _external=True,
                          **url_kwargs)
            post.url = url
            return post

        @classmethod
        def prepare_author(cls, author):
            """
            Prepare the author data
            """
            name = utils.slugify(author.name or "no-name")
            #url = url_for("%s:post_author" % view_name, id=author.id, name=name, _external=True)
            #author.url = url
            return author

        @classmethod
        def get_prev_next_post(cls, post, position):
            """
            Return previous or next post based on the current post
            :params post: post object
            :params position:
            """
            position = position.lower()
            if position not in ["prev", "next"]:
                 raise ValueError("Invalid position key. Must be 'prev' or 'next'")

            posts = Post.get_published(types=post_types)

            if position == "prev":
                posts = posts.filter(Post.id < post.id)
            elif position == "next":
                posts = posts.filter(Post.id > post.id)
            post = posts.first()
            return cls.prepare_post(post) if post else None

        @menu(endpoint=endpoint_namespace % "page_index", **_menu)
        @template(template_page % "page_index")
        @route(endpoint_path, endpoint=endpoint_namespace % "page_index")
        def page_index(self, endpoint=None):

            page = request.args.get("page", 1)
            app_per_page = get_config("APPLICATION_PAGINATION_PER_PAGE", 10)
            per_page = query.get("limit", app_per_page)

            set_meta(title=title, description=description)

            _query = {"types": query.get("types"),
                      "categories": query.get("categories"),
                      "tags": query.get("tags")}

            posts = Post\
                .get_published(**_query)\
                .order_by(query.get("order_by"))

            posts = posts.paginate(page=page,
                                   per_page=per_page,
                                   callback=self.prepare_post)
            _kwargs = {
                """
                "post_header": opt_endpoints.get("index.post_header", None),
                "post_subheader": opt_endpoints.get("index.post_subheader", None),
                "post_show_byline": opt_endpoints.get("index.post_show_byline", True)
                visible_with_
                """
            }
            _kwargs = dict()
            return dict(posts=posts, **_kwargs)

        @menu("%s Page" % _menu["name"],
              visible=False,
              endpoint=slug_format.get(slug).get("endpoint"),
              extends=view)  # No need to show the read in the menu
        @template(template_page % "page_single")
        @route(slug_format.get(slug).get("route"),
               endpoint=slug_format.get(slug).get("endpoint"))
        def page_single(self, id=None, slug=None, month=None, date=None):
            """
            Endpoints options
                single
                    - post_show_byline
            """
            post = None
            _q = {}
            if id:
                _q = {"id": id}
            elif slug:
                _q = {"slug": slug}

            post = Post.get_published(types=query.get("types"), **_q)
            if not post:
                abort("PublisherPageNotFound")

            set_meta(title=post.title,
                           image=post.top_image,
                           description=post.excerpt)

            _kwargs = {
                #"post_show_byline": opt_endpoints.get("single.post_show_byline", True)
            }
            _kwargs = dict()
            return dict(post=self.prepare_post(post), **_kwargs)

        @menu("%s Archive" % _menu["name"],
              visible=False,
              endpoint=endpoint_namespace % "page_archive",
              extends=view)
        @template(template_page % "page_archive")
        @route(endpoint_path + "archive/",
               endpoint=endpoint_namespace % "page_archive")
        def page_archive(self):

            set_meta(title="Archive")

            _query = {"types": query.get("types"),
                      "categories": query.get("categories"),
                      "tags": query.get("tags")}

            posts = Post.get_published(**_query)\
                .order_by(Post.published_at.desc())\
                .group_by(Post.db.func.year(Post.published_at),
                          Post.db.func.month(Post.published_at))

            return dict(posts=posts)

        '''
        @menu(opt_endpoints.get("authors.menu", "Authors"),
              visible=opt_endpoints.get("authors.show_menu", False),
              #order=opt_endpoints.get("authors.menu_order", 91),
              endpoint=endpoint_namespace % "post_authors",
              extends=view)
        @template(template_page % "post_authors")
        @route(opt_endpoints.get("authors.endpoint", "authors"),
               endpoint=endpoint_namespace % "post_authors")
        def post_authors(self):
            """
            Endpoints options
                - authors
                    menu
                    show_menu
                    menu_order
                    endpoint
                    title
            """

            set_meta(title=opt_endpoints.get("authors.title", "Authors"))

            authors = []
            return dict(authors=authors)

        @menu(opt_endpoints.get("author.menu", "Author"),
              visible=False,
              endpoint=endpoint_namespace % "post_author",
              extends=view)
        @template(template_page % "post_author")
        @route("%s/<id>/<name>" % opt_endpoints.get("author.endpoint", "author"),
               endpoint=endpoint_namespace % "post_author")
        def post_author(self, id, name=None):
            """
            Endpoints options
                - author
                    endpoint
            """

            set_meta(title=opt_endpoints.get("author.title", "Author"))

            author = []
            return dict(author=author)
        '''

    """
    method_name = namespace.lower()
    maps = {
        "page_index": "index"
    }
    new_class_page = type("Page" + namespace.capitalize(), (Page,), {})
    new_class_page.slug_format = slug_format
    new_class_page.slug = slug


    for k, v in maps.items():
        m = copy.deepcopy(getattr(new_class_page, k))
        key = method_name + "_" + v
        setattr(new_class_page, key, m)
        nm = getattr(new_class_page, k)
        #print(inspect.getargspec(nm))
        if v == "index":
            menu(options.get("menu"),
                  visible=True if options.get("menu") else False,
                  endpoint="Index:pages_index",
                  extends=view)(nm)
        template(template_page % "page_" + v)(nm)
        #route(endpoint_path, endpoint=endpoint_namespace % v)(nm)
    return new_class_page
    """



    return Page


# ------------------------------------------------------------------------------

def admin(view, **kwargs):

    route_base = "publisher-admin"
    PostModel = kwargs.get("model")

    template_dir = kwargs.get("template_dir", "Magic/Plugin/Publisher/Admin")
    template_page = template_dir + "/%s.html"

    _menu = kwargs.get("menu", {})
    _menu.setdefault("title", "Publisher")
    _menu.setdefault("group_name", "admin")
    _menu["visible_with_auth_user"] = True
    _user_roles = kwargs.get("user_roles", ('superadmin', 'admin', 'manager', 'editor'))

    # Create a Admin menu for all the methods in Admin
    @menu(**_menu)
    class PublisherAdminMenu(object): pass

    class Admin(object):

        decorators = view.decorators

        @menu("Posts", endpoint="PublisherAdmin:index", order=1, extends=PublisherAdminMenu)
        @template(template_page % "index")
        @require_user_roles(*_user_roles)
        @route("%s" % route_base, endpoint="PublisherAdmin:index")
        def publisher_admin_index(self):
            """
            List all posts
            """
            set_meta(title="All Posts")
            per_page = get_config("APPLICATION_PAGINATION_PER_PAGE", 25)
            page = request.args.get("page", 1)
            id = request.args.get("id", None)
            slug = request.args.get("slug", None)
            status = request.args.get("status", "all")
            user_id = request.args.get("user_id", None)
            type_id = request.args.get("type_id", None)
            category_id = request.args.get("category_id", None)
            tag_id = request.args.get("tag_id", None)

            reorder_post = request.args.get("reorder_post")

            posts = PostModel.Post.query()
            types = PostModel.Type.query().order_by("name asc")
            types_options = [(t.id, t.name) for t in types]

            selected_type = None
            if type_id:
                selected_type = PostModel.Type.get(type_id)

            if id:
                posts = posts.filter(PostModel.Post.id == id)
            if slug:
                posts = posts.filter(PostModel.Post.slug == slug)
            if user_id:
                posts = posts.filter(PostModel.Post.user_id == user_id)
            if type_id:
                type_id = int(type_id)
                posts = posts.filter(PostModel.Post.type_id == type_id)
            if category_id:
                posts = posts.join(PostModel.CategoryMap)\
                    .join(PostModel.Category)\
                    .filter(PostModel.Category.id == category_id)
            if tag_id:
                posts = posts.join(PostModel.TagMap)\
                    .join(PostModel.Tag)\
                    .filter(PostModel.Tag.id == tag_id)
            if status == "publish":
                posts = posts.filter(PostModel.Post.is_published == True)
            elif status == "draft":
                posts = posts.filter(PostModel.Post.is_draft == True)
            elif status == "revision":
                posts = posts.filter(PostModel.Post.is_revision == True)

            posts = posts.order_by(PostModel.Post.id.desc())
            posts = posts.paginate(page=page, per_page=per_page)

            return dict(posts=posts,
                        types=types,
                        types_options=types_options,
                        search=False,
                        query_vars={
                           "id": id,
                           "slug": slug,
                           "user_id": user_id,
                           "type_id": type_id,
                           "status": status
                        },
                        selected_type=selected_type)

        @menu("Post Preview", endpoint="PublisherAdmin:preview", visible=False, order=1, extends=PublisherAdminMenu)
        @template(template_page % "preview")
        @require_user_roles(*_user_roles)
        @route("%s/preview/<id>" % route_base, endpoint="PublisherAdmin:preview")
        def publisher_admin_preview(self, id):
            """
            Read Post
            """
            post = PostModel.Post.get(id)
            if not post:
                abort(404, "Post doesn't exist")

            set_meta(title="Read: %s " % post.title)

            return dict(post=post)

        @menu("Edit Post", endpoint="PublisherAdmin:edit", visible=False, extends=PublisherAdminMenu)
        @menu("New Post", endpoint="PublisherAdmin:new", order=2, extends=PublisherAdminMenu)
        @template(template_page % "edit")
        @require_user_roles(*_user_roles)
        @route("%s/new" % route_base, defaults={"id": None}, endpoint="PublisherAdmin:new")
        @route("%s/edit/<id>" % route_base, endpoint="PublisherAdmin:edit")
        def publisher_admin_edit(self, id):
            """
            Create / Edit Post
            """
            set_meta(title="Edit Post")

            types = [(t.id, t.name) for t in PostModel.Type.query().order_by(PostModel.Type.name.asc())]
            categories = [(c.id, c.name) for c in PostModel.Category.query().order_by(PostModel.Category.name.asc())]
            checked_cats = []

            type_id = request.args.get("type_id", None)

            # data to pass to view
            post = {
                "id": 0,
                "title": "",
                "content": "",
                "slug": "",
                "is_public": True,
                "is_sticky": False,
                "is_featured": False,
                "type_id": 0 if not type_id else int(type_id),
                "options": {}
            }

            # saved in session
            flashed_data = get_flashed_data()
            if request.args.get("error") and flashed_data:
                post = flashed_data
                checked_cats = post["post_categories"]

            elif id:
                post = PostModel.Post.get(id)
                if not post or post.is_revision:
                    abort(404, "Post doesn't exist")
                checked_cats = [c.id for c in post.categories]

            images = PostModel.UploadObject.query()\
                .filter(PostModel.UploadObject.type == "IMAGE")\
                .order_by(PostModel.UploadObject.name.asc())

            images_list = [{"id": img.id, "url": img.object_url} for img in images]
            return dict(post=post,
                        types=types,
                        categories=categories,
                        checked_categories=checked_cats,
                        images_list=images_list)

        @require_user_roles(*_user_roles)
        @route("%s/post" % route_base, methods=["POST"], endpoint="PublisherAdmin:post")
        def publisher_admin_post(self):
            id = request.form.get("id")
            title = request.form.get("title")
            slug = request.form.get("slug")
            content = request.form.get("content")
            description = request.form.get("description")
            type_id = request.form.get("type_id")
            post_categories = request.form.getlist("post_categories")
            published_date = request.form.get("published_date")
            status = request.form.get("status", "draft")
            is_published = True if status == "publish" else False
            is_draft = True if status == "draft" else False
            is_public = True if request.form.get("is_public") == "y" else False
            is_sticky = True if request.form.get("is_sticky") == "y" else False
            is_featured = True if request.form.get("is_featured") == "y" else False
            featured_image = request.form.get("featured_image")
            featured_embed = request.form.get("featured_embed")
            featured_media_top = request.form.get("featured_media_top", "")
            social_options = request.form.getlist("social_options")
            tags = list(set(request.form.get("tags", "").split(",")))

            now_dt = datetime.datetime.now()
            data = {
                "title": title,
                "content": content,
                "description": description,
                "featured_image": featured_image,
                "featured_embed": featured_embed,
                "featured_media_top": featured_media_top,
                "type_id": type_id,
                "is_sticky": is_sticky,
                "is_featured": is_featured,
                "is_public": is_public
            }

            if status in ["draft", "publish"] and (not title or not type_id):
                if not title:
                    flash("Post Title is missing ", "error")
                if not type_id:
                    flash("Post type is missing", "error")

                data.update({
                    "published_date": published_date,
                    "post_categories": post_categories,
                    "options": {"social_options": social_options},
                })
                flash_data(data)

                if id:
                    url = url_for("PublisherAdmin:edit", id=id, error=1)
                else:
                    url = url_for("PublisherAdmin:new", error=1)
                return redirect(url)

            published_date = datetime.datetime.strptime(published_date, "%Y-%m-%d %H:%M:%S") \
                if published_date else now_dt

            if id and status in ["delete", "revision"]:
                post = PostModel.Post.get(id)
                if not post:
                    abort(404, "Post '%s' doesn't exist" % id)

                if status == "delete":
                    post.delete()
                    flash("Post deleted successfully!", "success")
                    return redirect(url_for("PublisherAdmin:index"))

                elif status == "revision":
                    data.update({
                        "user_id": current_user.id,
                        "parent_id": id,
                        "is_revision": True,
                        "is_draft": False,
                        "is_published": False,
                        "is_public": False
                    })
                    post = PostModel.Post.create(**data)
                    return jsonify({"revision_id": post.id})

            elif status in ["draft", "publish"]:
                data.update({
                    "is_published": is_published,
                    "is_draft": is_draft,
                    "is_revision": False,
                    "is_public": is_public
                })

                if id:
                    post = PostModel.Post.get(id)
                    if not post:
                        abort(404, "Post '%s' doesn't exist" % id)
                    elif post.is_revision:
                        abort(403, "Can't access this post")
                    else:
                        if is_sticky and not post.is_sticky:
                            data["sticky_at"] = now_dt
                        if is_featured and not post.is_featured:
                            data["featured_at"] = now_dt
                        post.update(**data)
                else:
                    data["user_id"] = current_user.id
                    if is_published:
                        data["published_at"] = published_date
                    if is_sticky:
                        data["sticky_at"] = now_dt
                    if is_featured:
                        data["featured_at"] = now_dt
                    post = PostModel.Post.create(**data)

                # prepare tags
                _tags = []
                for tag in tags:
                    tag = tag.strip().lower()
                    _tag = PostModel.Tag.get_by_slug(name=tag)
                    if tag and not _tag:
                        _tag = PostModel.Tag.new(name=tag)
                    if _tag:
                        _tags.append(_tag.id)
                post.update_tags(_tags)

                post.set_slug(slug or title)
                post.update_categories(map(int, post_categories))
                post.set_options("social", social_options)

                if post.is_published and not post.published_at:
                        post.update(published_at=published_date)

                flash("Post saved successfully!", "success")

                return redirect(url_for("PublisherAdmin:edit", id=post.id))

            else:
                abort(400, "Invalid post status")

        @menu("Categories", endpoint="PublisherAdmin:categories", order=4, extends=PublisherAdminMenu)
        @template(template_page % "categories")
        @require_user_roles(*_user_roles)
        @route("%s/categories" % route_base, methods=["GET", "POST"], endpoint="PublisherAdmin:categories")
        def publisher_admin_categories(self):
            set_meta(title="Post Categories")
            if request.method == "POST":
                id = request.form.get("id", None)
                action = request.form.get("action")
                name = request.form.get("name")
                slug = request.form.get("slug", None)
                ajax = request.form.get("ajax", False)
                try:
                    if not id:
                        cat = PostModel.Category.new(name=name, slug=slug)
                        if ajax:
                            return jsonify({
                                "id": cat.id,
                                "name": cat.name,
                                "slug": cat.slug,
                                "status": "OK"
                            })
                        flash("New category '%s' added" % name, "success")
                    else:
                        post_cat = PostModel.Category.get(id)
                        if post_cat:
                            if action == "delete":
                                post_cat.delete()
                                flash("Category '%s' deleted successfully!" % post_cat.name, "success")
                            else:
                                post_cat.update(name=name, slug=slug)
                                flash("Category '%s' updated successfully!" % post_cat.name, "success")
                except Exception as ex:
                    if ajax:
                        return jsonify({
                            "error": True,
                            "error_message": ex.message
                        })

                    flash("Error: %s" % ex.message, "error")
                return redirect(url_for("PublisherAdmin:categories"))

            else:
                cats = PostModel.Category.query().order_by(PostModel.Category.name.asc())
                return dict(categories=cats)

        @menu("Tags", endpoint="PublisherAdmin:tags", order=5, extends=PublisherAdminMenu)
        @template(template_page % "tags")
        @require_user_roles(*_user_roles)
        @route("%s/tags" % route_base, methods=["GET", "POST"], endpoint="PublisherAdmin:tags")
        def publisher_admin_tags(self):
            set_meta(title="Post Tags")
            if request.method == "POST":
                id = request.form.get("id", None)
                action = request.form.get("action")
                name = request.form.get("name")
                slug = request.form.get("slug", None)
                ajax = request.form.get("ajax", False)
                try:
                    if not id:
                        tag = PostModel.Tag.new(name=name, slug=slug)
                        if ajax:
                            return jsonify({
                                "id": tag.id,
                                "name": tag.name,
                                "slug": tag.slug,
                                "status": "OK"
                            })
                        flash("New Tag '%s' added" % name, "success")
                    else:
                        post_tag = PostModel.Tag.get(id)
                        if post_tag:
                            if action == "delete":
                                post_tag.delete()
                                flash("Tag '%s' deleted successfully!" % post_tag.name, "success")
                            else:
                                post_tag.update(name=name, slug=slug)
                                flash("Tag '%s' updated successfully!" % post_tag.name, "success")
                except Exception as ex:
                    if ajax:
                        return jsonify({
                            "error": True,
                            "error_message": ex.message
                        })

                    flash("Error: %s" % ex.message, "error")
                return redirect(url_for("PublisherAdmin:tags"))

            else:
                tags = PostModel.Tag.query().order_by(PostModel.Tag.name.asc())
                return dict(tags=tags)

        @menu("Types", endpoint="PublisherAdmin:types", order=6, extends=PublisherAdminMenu)
        @template(template_page % "types")
        @require_user_roles(*_user_roles)
        @route("%s/types" % route_base, methods=["GET", "POST"], endpoint="PublisherAdmin:types")
        def publisher_admin_types(self):
            set_meta(title="Post Types")
            if request.method == "POST":
                try:
                    id = request.form.get("id", None)
                    action = request.form.get("action")
                    name = request.form.get("name")
                    slug = request.form.get("slug", None)
                    if not id:
                        PostModel.Type.new(name=name, slug=slug)
                        flash("New type '%s' added" % name, "success")
                    else:
                        post_type = PostModel.Type.get(id)
                        if post_type:
                            if action == "delete":
                                post_type.delete()
                                flash("Type '%s' deleted successfully!" % post_type.name, "success")
                            else:
                                post_type.update(name=name, slug=slug)
                                flash("Type '%s' updated successfully!" % post_type.name, "success")
                except Exception as ex:
                    flash("Error: %s" % ex.message, "error")
                return redirect(url_for("PublisherAdmin:types"))
            else:
                types = PostModel.Type.query().order_by(PostModel.Type.name.asc())
                return dict(types=types)

        @menu("Images", endpoint="PublisherAdmin:images", order=3, extends=PublisherAdminMenu)
        @template(template_page % "images")
        @require_user_roles(*_user_roles)
        @route("%s/images" % route_base, methods=["GET", "POST"], endpoint="PublisherAdmin:images")
        def publisher_admin_images(self):
            set_meta(title="Images")
            if request.method == "POST":
                id = request.form.get("id", None)
                action = request.form.get("action")
                description = request.form.get("description")
                if id:
                    image = PostModel.UploadObject.get(id)
                    if image:
                        if action == "delete":
                            image.delete()
                            obj = storage.get(image.name)
                            if obj:
                                obj.delete()
                            flash("Image deleted successfully!", "success")
                        else:
                            image.update(description=description)
                            flash("Image updated successfully!", "success")
                else:
                    abort(404, "No image ID provided")
                return redirect(url_for("PublisherAdmin:images"))

            else:
                page = request.args.get("page", 1)
                per_page = get_config("PAGINATION_PER_PAGE", 25)
                images = PostModel.UploadObject.query()\
                    .filter(PostModel.UploadObject.type == "IMAGE")\
                    .order_by(PostModel.UploadObject.name.asc())
                images = images.paginate(page=page, per_page=per_page)
                return dict(images=images)

        @require_user_roles(*_user_roles)
        @route("%s/upload-image" % route_base, methods=["POST"], endpoint="PublisherAdmin:upload_image")
        def publisher_admin_upload_image(self):
            """
            Placeholder for markdown
            """
            try:
                ajax = request.form.get("ajax", False)
                allowed_extensions = ["gif", "png", "jpg", "jpeg"]

                if request.files.get("file"):
                    _file = request.files.get('file')
                    obj = storage.upload(_file,
                                         prefix="publisher-uploads/",
                                         allowed_extensions=allowed_extensions,
                                         public=True)

                    if obj:
                        description = os.path.basename(obj.name)
                        description = description.replace(".%s" % obj.extension, "")
                        description = description.split("__")[0]
                        upload_object = PostModel.UploadObject.create(name=obj.name,
                                                                      provider=obj.provider_name,
                                                                      container=obj.container.name,
                                                                      extension=obj.extension,
                                                                      type=obj.type,
                                                                      object_path=obj.path,
                                                                      object_url=obj.url,
                                                                      size=obj.size,
                                                                      description=description)
                        if ajax:
                            return jsonify({
                                "id": upload_object.id,
                                "url": upload_object.object_url
                            })
                        else:
                            flash("Image '%s' uploaded successfully!" % upload_object.name, "success")
                else:
                    flash("Error: Upload object file is invalid or doesn't exist", "error")
            except Exception as e:
                flash("Error: %s" % e.message, "error")
            return redirect(url_for("PublisherAdmin:images"))

    return Admin


# ------------------------------------------------------------------------------
# Utils script to setup the Publisher
def setup(model, admin_user_id, post_types=[], post_categories=[]):

    # Set types
    if not model.Type.query().count():
        [model.Type.new(t) for t in post_types]

    # Set categories
    if not model.Category.query().count():
        [model.Category.new(c) for c in post_categories]

    # Add some basic post
    if not model.Post.query().count():
        posts = [
            {
                "title": "About Us",
                "slug": "about",
                "content": "**About Us**",
                "type_slug": "document",
                "is_published": True,
                "user_id": admin_user_id,
            },
            {
                "title": "Terms of Service",
                "slug": "tos",
                "content": "**Terms of Service**",
                "type_slug": "document",
                "is_published": True,
                "user_id": admin_user_id,
            },
            {
                "title": "Privacy",
                "slug": "privacy",
                "content": "**Privacy Policy**",
                "type_slug": "document",
                "is_published": True,
                "user_id": admin_user_id,
            },
            {
                "title": "First Page",
                "slug": "first-page",
                "content": "**This is our First Page!**",
                "type_slug": "page",
                "is_published": True,
                "user_id": admin_user_id,
            },
            {
                "title": "First Blog",
                "slug": "first-blog",
                "content": "**This is our First Blog!**",
                "type_slug": "blog",
                "is_published": True,
                "user_id": admin_user_id,
            }
        ]
        [model.Post.new(**post) for post in posts]
    return True
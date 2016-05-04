from os import path, mkdir

from django.core.management.base import BaseCommand, CommandError


BLOG_BASE_CONTENT = """{% extends "base.html" %}{# <--- UPDATE THIS #}
{# This is the base template for your blog. It should inherit from your current site-wide base template. #}


{% block title %}Blog powered by Butter CMS{% endblock %}
{% block description %}This is another snazzy blog powered by Butter CMS.{% endblock %}


{% block content %}{# <--- UPDATE THIS #}
{# This block name should be whatever your main content block is called in your base.html file. This is where your blog content will appear. #}
{# By default we use the name 'content' since that's most common. #}


{% comment %}
<!-- Here is an example of adding a side bar to your blog. 
Customize this with your own CSS, copy, and call to action (sign up, email subscribe, etc). -->
{% block blog_sidebar %}
<div class="sidebar">
    <h4>Welcome to our blog!</h4>
    <a href="#">You should sign up for our service.</a>
</div>
{% endblock %}
{% endcomment %}



<div class='blog-wrapper'>
{% block blog_content %}
    <!-- This is where all of your blog content (home page, post, author, cateogry, etc) will show up. -->

    <!-- Here we loop over all of your recent blog posts. -->
    {% for post in recent_posts %}
        {% include "blog/blog_post_list_entry.html" with post=post %}
    {% endfor %}

    {% include "blog/pagination_controls.html" %}
{% endblock %}
</div>

{% endblock %}
"""


BLOG_PAGINATION_CONTROLS = """<!-- Pagination controls when there are more than 10 posts -->
<ul class="pager">
    {% if next_page %}
    <li class="previous"><a href="{% url "archive" next_page %}">&laquo; Older posts</a></li>
    {% endif %} 

    {% if previous_page %}
    <li class="next"><a href="{% url "archive" previous_page %}">Newer posts &raquo;</a></li>
    {% endif %}
</ul>"""


BLOG_POST_LIST_ENTRY = """<div class="post-preview">
    <a href="{% url 'blog_post' post.slug %}">
      <h3 class="post-title">{{ post.title }}</h3>
    </a>
    
    <p class="post-byline">
        Posted by <a href="{% url 'blog_author' post.author.slug %}">{{ post.author.first_name }} {{ post.author.last_name }}</a>
     on {{ post.published }}
        <span class="text-muted"> in </span>
        
        {% for category in post.categories %}
            <span><a href="{% url 'blog_category' category.slug %}">{{category.name}}</a></span>
        {% endfor %}
    </p>

    <p class="post-summary">{{ post.summary }}</p>
</div>
<hr>
"""


BLOG_POST_CONTENT = """{% extends "blog/blog_base.html" %}

{% block title %}{{ post.seo_title }}{% endblock %}
{% block description %}{{ post.meta_description }}{% endblock %}

{% block blog_content %}
<!--
To see a full list of attributes availabile on "post" in this template,
enter that post slug here:  https://buttercms.com/docs/api/#!/posts/Blog_Post_retrieve

You'll get a real-time response from our API.
-->

<!-- The Butter editor supports image alignment. When an image is left aligned, we apply a "butter-float-left" class to a div tag surrounding the image. When right aligned, we apply "butter-float-right". These are reasonable default styles you'll probably want to put into a proper .css file -->
<style type="text/css">
@media only screen and (min-width: 420px)  {
    .butter-float-left {
        float: left;
        margin: 0px 10px 10px 0px;
    }

    .butter-float-right {
        float: right;
        margin: 0px 0px 10px 10px;
    }
}
</style>


<div class="post">
    <h2 class="post-title">{{ post.title }}</h2>
    
    <p class="post-byline">
        Posted by 
        <a href="{% url 'blog_author' post.author.slug %}">{{ post.author.first_name }} {{ post.author.last_name }}</a>
    
        <span class="text-muted"> in </span>
        {% for category in post.categories %}
            <span class="label label-default"><a href="{% url 'blog_category' category.slug %}">{{category.name}}</a></span>
        {% endfor %}
    </p>

    <div class="post-body">{{ post.body }}</div>
</div>

<ul class="pager">
    {% if post.previous_post %}
    <li class="previous"><a href="{% url 'blog_post' post.previous_post.slug %}">&laquo; Previous post</a></li>
    {% endif %} 

    {% if post.next_post %}
    <li class="next"><a href="{% url 'blog_post' post.next_post.slug %}">Next post &raquo;</a></li>
    {% endif %}
</ul>

<!-- 
// For post comments, we recommend https://disqus.com/ 
// Create a Disqus account and paste your embed code below.
// Here's a sample
<hr>
<div id="disqus_thread"></div>
<script type="text/javascript">
    /* * * CONFIGURATION VARIABLES * * */
    var disqus_shortname = 'XXXXXXXX';
    
    /* * * DON'T EDIT BELOW THIS LINE * * */
    (function() {
        var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
        dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
        (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
    })();
</script>
-->

{% endblock %}
"""


BLOG_AUTHOR = """{% extends "blog/blog_base.html" %}

{% block title %}Recent posts from {{ first_name }} {{ last_name }}{% endblock %}
{% block description %}Recent blog posts written by {{ first_name }} {{ last_name }}.{% endblock %}

{% block blog_content %}
<h2>Recent posts by {{ first_name }} {{ last_name }} ({{ email }})</h2>
{% for post in recent_posts %}
    {% include "blog/blog_post_list_entry.html" with post=post %}
{% endfor %}

{% include "blog/pagination_controls.html" %}

{% endblock %}
"""


BLOG_CATEGORY = """{% extends "blog/blog_base.html" %}

{% block title %}Recent {{category_name}} posts{% endblock %}
{% block description %}Recent blog posts written in the {{category_name}} category.{% endblock %}

{% block blog_content %}
<h2>Recent {{category_name}} posts</h2>
{% for post in recent_posts %}
    {% include "blog/blog_post_list_entry.html" with post=post %}
{% endfor %}

{% include "blog/pagination_controls.html" %}

{% endblock %}
"""


class Command(BaseCommand):

    help = """ Scaffolds a default set of templates for your Butter CMS blog. 
        This includes:
        <app>/templates/blog/blog_base.html
        <app>/templates/blog/blog_post_list_entry.html
        <app>/templates/blog/pagination_controls.html
        <app>/templates/blog/blog_post.html
        <app>/templates/blog/blog_author.html
        <app>/templates/blog/blog_category.html
        """

    args = '<appname>'


    def handle(self, *args, **options):
        try:
            app_name = args[0]
        except IndexError:
            raise CommandError('Pass in app name for blog directory creation:  python manage.py butter_templates <app_name>')

        print "Whipping up Butter..."
       
        # Check if template dir exists. If it does, then we create a blog directory within it.
        template_directory = '{0}/templates/'.format(app_name)

        if path.exists(template_directory):
            print 'Great, {0} exists. Creating blog/ directory within it...'.format(template_directory)
            
            blog_directory = '{0}blog/'.format(template_directory)

            if not path.exists(blog_directory):
                # Create the directory and all inital files within it.
                mkdir(blog_directory)
                print 'Created {0}'.format(blog_directory)

            
            # Create each template file, but only if it doesn't already exist.

            # Blog base
            if not path.exists('{0}blog_base.html'.format(blog_directory)):
                with open('{0}blog_base.html'.format(blog_directory), 'w') as fp:
                    fp.write(BLOG_BASE_CONTENT)
                print 'Created {0}blog_base.html'.format(blog_directory)
            else:
                print 'Skipping {0}blog_base.html because it already exists.'.format(blog_directory)

            # Blog post list entry (used in blog base)
            if not path.exists('{0}blog_post_list_entry.html'.format(blog_directory)):
                with open('{0}blog_post_list_entry.html'.format(blog_directory), 'w') as fp:
                    fp.write(BLOG_POST_LIST_ENTRY)
                print 'Created {0}blog_post_list_entry.html'.format(blog_directory)
            else:
                print 'Skipping {0}blog_post_list_entry.html because it already exists.'.format(blog_directory)

            # Pagination controls
            if not path.exists('{0}pagination_controls.html'.format(blog_directory)):
                with open('{0}pagination_controls.html'.format(blog_directory), 'w') as fp:
                    fp.write(BLOG_PAGINATION_CONTROLS)
                print 'Created {0}pagination_controls.html'.format(blog_directory)
            else:
                print 'Skipping {0}pagination_controls.html because it already exists.'.format(blog_directory)

            # Blog post
            if not path.exists('{0}blog_post.html'.format(blog_directory)):
                with open('{0}blog_post.html'.format(blog_directory), 'w') as fp:
                    fp.write(BLOG_POST_CONTENT)
                print 'Created {0}blog_post.html'.format(blog_directory)
            else:
                print 'Skipping {0}blog_post.html because it already exists.'.format(blog_directory)

            # Author page
            if not path.exists('{0}blog_author.html'.format(blog_directory)):
                with open('{0}blog_author.html'.format(blog_directory), 'w') as fp:
                    fp.write(BLOG_AUTHOR)
                print 'Created {0}blog_author.html'.format(blog_directory)
            else:
                print 'Skipping {0}blog_author.html because it already exists.'.format(blog_directory)

            # Category page
            if not path.exists('{0}blog_category.html'.format(blog_directory)):
                with open('{0}blog_category.html'.format(blog_directory), 'w') as fp:
                    fp.write(BLOG_CATEGORY)
                print 'Created {0}blog_category.html'.format(blog_directory)
            else:
                print 'Skipping {0}blog_category.html because it already exists.'.format(blog_directory)

            print 'All done! Check out the files created in {0}'.format(blog_directory)

        else:
            raise CommandError('{0} does not exist. Please ensure {1} is an app and that it\'s folder exists.'.format(template_directory, app_name))

      


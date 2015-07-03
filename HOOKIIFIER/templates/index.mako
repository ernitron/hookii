<%inherit file="base.mako"/>

<span class='col1'>Articolo</span>
<span class='col2'>Pubblicato il</span>
<span class='col3'>Commenti</span>
<hr />

% for p in posts:
<span class='col1'><a href='${p["post_name"]}.html'> ${p["post_title"]} </a></span>
<span class='col2'> ${p["post_date"]} </span>
<span class='col3'><b> ${p["comment_count"]} </b></span>
<hr />
% endfor

<span class='col1'><b> ${total_posts} Total articles archived </b></span>
<span class='col2'></span>
<span class='col3'></span>
<hr />

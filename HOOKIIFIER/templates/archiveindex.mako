<%inherit file="base.mako"/>

<span class='col1'>Articolo</span>
<span class='col2'>Pubblicato il</span>
<span class='col3'>Commenti</span>
<hr />

% for art in articles:
<span class='col1'><a href='${art["post_name"]}.html'> ${art["post_title"]} </a></span>
<span class='col2'> ${art["post_date"]} </span>
<span class='col3'><b> ${art["comment_count"]} </b></span>
<hr />
% endfor

<span class='col1'><b> ${total_articles} Total articles archived </b></span>
<span class='col2'></span>
<span class='col3'></span>
<hr />

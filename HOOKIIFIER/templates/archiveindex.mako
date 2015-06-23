<%inherit file="base.mako"/>

<span class='col1'>Articolo</span>
<span class='col2'>Pubblicato il</span>
<span class='col3'>Commenti</span>
<hr />

% for art in articles:
<span class='col1'><a href='${art["pname"]}.html'> ${art["ptitle"]} </a></span>
<span class='col2'> ${art["pdate"]} </span>
<span class='col3'><b> ${art["pcount"]} </b></span>
<hr />
% endfor

<span class='col1'><b> ${total_articles} Total articles archived </b></span>
<span class='col2'></span>
<span class='col3'></span>
<hr />

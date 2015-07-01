<%inherit file="base.mako"/>

<%
    import HOOKIIFIER.filters as filters
%>

<div class='hookii-article'>
    <h2 style='margin-bottom:0.1em;'>
        <a href='http://www.hookii.it/${pname}'>${ptitle}</a>
    </h2>
    <p style='margin-top:0.1em;'>
        <font size='2'>Comparso il ${pdate} su <a href='http://www.hookii.it/'>hookii.</a></font>
        Vai all'articolo <a href='http://www.hookii.it/${pname}'>${pname}</a> per commentare.
    </p>

    <p>
        ${pcontent}
    <p>
</div>

<hr>

<h3>
    ${pcount} ${"commenti" if pcount != 1 else "commento"}
</h3>

<div class='hookii-comment'>
    % for com in comments:
        <div style="margin-left:${com["margin"]}px; margin-right:-${com["margin"]}px; width:80%%;">
            <h4 style='margin-bottom:0.1em;'>
                <a href='http://www.hookii.it/${pname}/#comment-${com["disqid"]}'>
                % if com["cauthor"] == com["cpauthor"]:
                    ${com["cauthor"]}
                % else:
                    ${"&#8627; %s &#8614; %s " % (com["cauthor"], com["cpauthor"])}
                % endif
                </a>
                <p style='margin-top:0.1em; font-size:80%%'>${com["cdate"]}</p>
            </h4>
            <p>${com["ccontent"] | filters.url, filters.disqus_user, filters.email_antispam }</p> 
            <hr>
        </div>
    % endfor
</div>

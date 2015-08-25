<%inherit file="base.mako"/>

<%
try:
    from HOOKIIFIER import filters
except ImportError:
    import filters
%>

<div class='hookii-article'>
    <h2 style='margin-bottom:0.1em;'>
        <a href='http://www.hookii.it/${post["post_name"]}'>${post["post_title"]}</a>
    </h2>
    <p style='margin-top:0.1em; font-size:80%'>
        Comparso il ${post["post_date"]} su <a href='http://www.hookii.it/'>hookii.</a>
        Vai all'articolo <a href='http://www.hookii.it/${post["post_name"]}'>${post["post_name"]}</a> per commentare.
    </p>

    <p>
        ${post["post_content"] | filters.email_antispam, filters.newline}
    <p>
</div>

<hr>

<h3>
    ${post["comment_count"]} ${"commenti" if post["comment_count"] != 1 else "commento"}
</h3>

<hr>

<div class='hookii-comment'>
    % for com in comments:
        <div style="margin-left:${com["level"]*20}px; margin-right:-${com["level"]*20}px; width:80%;">
            <h4 style='margin-bottom:0.1em;'>
                % if com["comment_type"] == "liveblog":
                    <a href='http://www.hookii.it/${post["post_name"]}/#liveblog-entry-${com["comment_id"]}'>
                    [LIVEBLOG]
                % else:
                    <a href='http://www.hookii.it/${post["post_name"]}/#comment-${com["comment_disqusid"]}'>
                % endif
                % if "parent_author" not in com:
                    ${com["comment_author"]}
                % else:
                    ${"&#8627; %s &#8614; %s " % (com["comment_author"], com["parent_author"])}
                % endif
                </a>
            </h4>
            <p style='margin-top:0.1em; font-size:80%'>${com["comment_date"]}</p>
            <p>${com["comment_content"] | filters.url, filters.disqus_user, filters.email_antispam, filters.newline }</p> 
            <hr>
        </div>
    % endfor
</div>

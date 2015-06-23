<html>
<head>
    <title>${title}</title>
    <meta name="generator" content="hookiifier">
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <meta name="robots" content="index, follow">
    <meta name="keywords" content="commenti, liberi, lettori, commenti giornali online, community, hookii">
    <meta name="description" content="${title}">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="html5.css">
    <!-- All in one Favicon 4.3 -->
    <link rel="shortcut icon" href="http://www.hookii.it/wp-content/uploads/2014/12/favicon14.ico" />
    <link rel="icon" href="http://www.hookii.it/wp-content/uploads/2014/12/favicon14.ico" type="image/gif"/>
    <link rel="apple-touch-icon" href="http://www.hookii.it/wp-content/uploads/2014/12/muccaipod.png" />
    <style>
    .col1 { width: 50%%; display: inline-block; color:#444; }
    .col2 { width: 20%%; display: inline-block; color:#444; }
    .col3 { width: 5%%; text-align: right; display: inline-block; color:#444; }
    </style>
</head>

<body>
    <header class="w3-container w3-theme-hookii">
    <%block name="header">
        <h1>
            <a href='http://www.hookii.it/' style='text-decoration: none; color: white;'>Hookii</a>
            <a href='http://www.hookii.it/archived' style='text-decoration: none; color: white;'> Archive </a>
            <font size='4' style='color: white'><i>Yes, we post!</font></i></a>
        </h1>
    </%block>
    </header>
    
    ${self.body()}
    
    <footer class="w3-container w3-theme-hookii">
    <%block name="footer">
        <a href='http://www.hookii.it/' style='color: white; font-size:80%%'>Hookii</a>
        Dookii productions &copy; 2014 - Generated on ${gentime}
    </%block>
    </footer>
</body>
</html>

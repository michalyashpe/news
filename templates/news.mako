<html>
<head>
    <meta charset="utf-8">
    <title>News Feed</title>
    <style>
        body {
            font-family: "Times New Roman", serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            direction: rtl;
            background: #f9f7f1;
        }
        h1 {
            text-align: center;
            font-size: 48px;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
        }
        .last-updated {
            text-align: center;
            font-size: 14px;
            color: #666;
            margin-top: -10px;
            margin-bottom: 20px;
        }
        .item {
            border-bottom: 1px solid #ccc;
            padding: 20px 0;
            column-count: 2;
            column-gap: 40px;
        }
        h2 {
            margin: 0 0 10px 0;
            font-size: 24px;
        }
        p {
            line-height: 1.6;
            margin: 0 0 10px 0;
        }
        a {
            color: #444;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>חדשות</h1>
    <div class="last-updated">עודכן לאחרונה: ${last_update_time}</div>
    % for item in items:
    <div class="item">
        <h2>${item[1]}</h2>
        <p>מקור: ${item[3]} | ${item[4]}</p>
        <p><a href="${item[2]}" target="_blank">קרא עוד</a></p>
    </div>
    % endfor
</body>
</html> 
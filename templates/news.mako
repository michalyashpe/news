<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
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
            font-size: 2.5rem;
            border-bottom: 2px solid #000;
            padding-bottom: 10px;
            margin: 0 0 20px 0;
        }
        .last-updated {
            text-align: center;
            font-size: 0.875rem;
            color: #666;
            margin-bottom: 20px;
        }
        .item {
            border-bottom: 1px solid #ccc;
            padding: 20px 0;
            break-inside: avoid;
        }
        h2 {
            margin: 0 0 10px 0;
            font-size: 1.25rem;
            line-height: 1.4;
        }
        .source-line {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
            font-size: 0.9rem;
            color: #666;
        }
        .source {
            font-weight: bold;
        }
        .date {
            direction: ltr;
            unicode-bidi: bidi-override;
        }
        p {
            line-height: 1.6;
            margin: 0 0 10px 0;
            font-size: 1rem;
        }
        a {
            color: #444;
            text-decoration: none;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }

        /* Mobile styles */
        @media (max-width: 768px) {
            body {
                padding: 10px;
            }
            h1 {
                font-size: 2rem;
                padding-bottom: 8px;
            }
            .item {
                padding: 15px 0;
            }
            h2 {
                font-size: 1.1rem;
            }
            p {
                font-size: 0.9rem;
            }
        }

        /* Small mobile devices */
        @media (max-width: 480px) {
            h1 {
                font-size: 1.75rem;
            }
            .item {
                padding: 12px 0;
            }
            h2 {
                font-size: 1rem;
            }
            p {
                font-size: 0.85rem;
            }
        }
    </style>
</head>
<body>
    <h1>חדשות</h1>
    <div class="last-updated">עודכן לאחרונה: ${last_update_time}</div>
    % for item in items:
    <div class="item">
        <h2>${item[1]}</h2>
        <div class="source-line">
            <span class="source">מקור: ${item[3]}</span>
            <span class="date">${item[4]}</span>
        </div>
        <p><a href="${item[2]}" target="_blank">קרא עוד</a></p>
    </div>
    % endfor
</body>
</html> 
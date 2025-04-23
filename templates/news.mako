<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>רק כותרות</title>
    <link rel="icon" type="image/png" href="/static/favicon.png">
    <link rel="apple-touch-icon" href="/static/favicon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Alef:wght@400;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: "Alef", "Arial", sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            direction: rtl;
            background: #f9f7f1;
        }
        h1 {
            text-align: center;
            font-size: 2.5rem;
            padding-bottom: 10px;
            margin: 0 0 10px 0;
            display: flex;
            align-items: center;
            justify-content: space-between;
            position: relative;
        }
        .last-updated {
            font-size: 0.875rem;
            color: #666;
            position: absolute;
            left: 0;
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            line-height: 1.2;
        }
        .last-updated-title {
            font-weight: bold;
        }
        .last-updated-time {
            font-size: 0.8rem;
        }
        .title {
            flex: 1;
            text-align: center;
        }
        .item {
            padding: 0;
            break-inside: avoid;
        }
        h2 {
            margin: 0;
            font-size: 1.1rem;
            line-height: 1.4;
            font-weight: 400;
        }
        .headline-link {
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: row-reverse;
            padding: 10px;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            margin-bottom: 10px;
            gap: 15px;
        }
        .headline-link:hover {
            background: #f5f5f5;
            border-color: #ccc;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .source-info {
            display: flex;
            flex-direction: column;
            justify-content: center;
            min-width: 80px;
            text-align: left;
            border-right: 1px solid #eee;
            padding-right: 10px;
        }
        .source {
            font-weight: 700;
            font-size: 0.85rem;
            color: #444;
        }
        .date {
            direction: ltr;
            unicode-bidi: bidi-override;
            font-size: 0.75rem;
            color: #888;
        }
        .headline-content {
            flex: 1;
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
                padding: 0;
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
                padding: 0;
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
    <h1>
        <span class="last-updated">
            <span class="last-updated-title">עודכן לאחרונה</span>
            <span class="last-updated-time">${last_update_time}</span>
        </span>
        <span class="title">רק כותרות</span>
    </h1>
    % for item in items:
    <div class="item">
        <a href="${item[2]}" target="_blank" class="headline-link">
            <div class="source-info">
                <span class="source">${item[3]}</span>
                <span class="date">${item[4].split()[0].split('-')[2]}/${item[4].split()[0].split('-')[1]} ${item[4].split()[1][:5]}</span>
            </div>
            <div class="headline-content">
                <h2>${item[1]}</h2>
            </div>
        </a>
    </div>
    % endfor
</body>
</html> 
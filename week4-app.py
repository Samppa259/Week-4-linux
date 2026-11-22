
import os
import pymysql
from flask import Flask

app = Flask(__name__)


def get_visitor_count():
    connection = pymysql.connect(
        host="localhost",
        user="week4reader",
        password=os.environ["DB_PASSWORD"],
        database="week2db"
    )

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT count FROM visitors WHERE id = 1")
            result = cursor.fetchone()
            return result[0] if result else 0
    finally:
        connection.close()


@app.route("/")
def index():
    count = get_visitor_count()

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Week 4 - Server Replication</title>

    <style>
        body {{
            font-family: Arial, sans-serif;
            background: #f0f4f8;
            color: #203040;
            margin: 0;
            line-height: 1.6;
        }}

        header {{
            background: #203040;
            color: white;
            text-align: center;
            padding: 30px 15px;
        }}

        main {{
            max-width: 950px;
            margin: 30px auto;
            padding: 25px;
            background: white;
            border-radius: 12px;
        }}

        h2 {{
            color: #1769aa;
            border-bottom: 2px solid #dce6ef;
            padding-bottom: 6px;
            margin-top: 30px;
        }}

        .counter {{
            background: #e4f3e8;
            border: 2px solid #70b982;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
        }}

        .count {{
            font-size: 42px;
            font-weight: bold;
            color: #176b35;
        }}

        .info {{
            background: #f0f4f8;
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
            overflow-wrap: anywhere;
        }}

        code {{
            background: #e1e8ef;
            padding: 3px 6px;
            border-radius: 4px;
        }}

        footer {{
            text-align: center;
            padding: 20px;
            color: #64748b;
        }}
    </style>
</head>

<body>

<header>
    <h1>Week 4 - Server Replication</h1>
    <p>Linux Server Administration Project</p>
</header>

<main>

    <div class="counter">
        <h2 style="border: none; margin-top: 0;">
            Website Visitor Counter
        </h2>
        <div class="count">{count}</div>
        <p>
            Current visitor count read from the MariaDB
            replica on Server B.
        </p>
        <p>
            This counter is read-only. Refreshing this page
            does not increase the count.
        </p>
    </div>


    <h2>1. How Server B Was Created</h2>

    <p>
        Server B was created as a second virtual machine
        in CSC cPouta. It uses Ubuntu 26.04.1 LTS,
        just like Server A.
    </p>

    <p>
        The second server was configured with MariaDB,
        Nginx, Python and Flask. It was connected to
        Server A using a private network connection.
    </p>

    <p>
        SSH key authentication was configured so that
        Server A can connect securely to Server B.
        This connection is used by the rsync backup script.
    </p>

    


    <h2>2. Storage Layout and Backup Locations</h2>

    <h3>Server A - Primary Server</h3>

    <p>
        Server A contains the original website files
        and the primary MariaDB database.
    </p>

    <ul>
        <li><code>/var/www/html/</code> - Website files.</li>
        <li><code>/home/ubuntu/viikko2/</code> - Week 2 Flask application.</li>
        <li><code>/home/ubuntu/viikko3.sh</code> - Week 3 report script.</li>
        <li><code>/home/ubuntu/backup-website.sh</code> - Website backup script.</li>
        <li><code>/var/lib/mysql/</code> - Default MariaDB data directory.</li>
        <li><code>/srv/backups/</code> - Not used for the remote website backups.</li>
    </ul>

    <h3>Server B - Replica and Backup Server</h3>

    <ul>
        <li><code>/srv/backups/website/</code> - Received website backups.</li>
        <li><code>/home/ubuntu/viikko4/</code> - Week 4 Flask application.</li>
        <li><code>/var/lib/mysql/</code> - Default MariaDB data directory.</li>
    </ul>

    <p>
        Each website backup is stored in its own
        timestamped directory under
        <code>/srv/backups/website/</code>.
        This allows older backups to be kept separately.
    </p>


    <h2>3. Linux Users, Database Users and Permissions</h2>

    <h3>Linux Users</h3>

    <p>
        The Linux user <code>ubuntu</code> is used to
        manage the applications and run the website
        backup script.
    </p>

    <p>
        The Week 4 Flask service also runs as
        <code>ubuntu</code>. Administrative configuration
        changes use <code>sudo</code>.
    </p>

    <h3>Database Users</h3>

    <div class="info">
        <strong>replication</strong><br>
        Used by Server B to receive database replication
        from Server A. It has the REPLICATION SLAVE privilege.
    </div>

    <div class="info">
        <strong>week2counter</strong><br>
        Used by the Week 2 application on Server A.
        It has SELECT and UPDATE permissions on
        <code>week2db.visitors</code>, allowing the
        visitor counter to increase.
    </div>

    <div class="info">
        <strong>week4reader</strong><br>
        Used by the Week 4 application on Server B.
        It has only SELECT permission on
        <code>week2db.visitors</code>. It can read
        the visitor count but cannot change it.
    </div>

    <h3>Ownership and File Permissions</h3>

    <ul>
        <li>
            The backup directory on Server B is owned by
            <code>ubuntu</code>.
        </li>
        <li>
            The <code>/srv/backups</code> directory has
            permission <code>700</code>, so only its owner
            has access.
        </li>
        <li>
            The database environment files
            <code>/etc/viikko2.env</code> and
            <code>/etc/viikko4.env</code> are owned by
            <code>root</code> and have permission
            <code>600</code>.
        </li>
        <li>
            The environment files contain database passwords
            and are not stored in the public website directory.
        </li>
    </ul>


    <h2>4. Hourly Backups and Continuous Replication</h2>

    <h3>Automatic Website Backups</h3>

    <p>
        A Bash script called
        <code>backup-website.sh</code> runs on Server A.
        It uses rsync over SSH to copy the website files
        to Server B.
    </p>

    <p>
        Cron runs the backup script once every hour.
        The cron entry is:
    </p>

    <div class="info">
        <code>0 * * * * /home/ubuntu/backup-website.sh</code>
    </div>

    <p>
        Each backup receives a timestamped directory name.
        The script also writes backup results to
        <code>/home/ubuntu/backup-website.log</code>.
    </p>

    <h3>Continuous Database Replication</h3>

    <p>
        MariaDB replication runs continuously between
        Server A and Server B.
    </p>

    <p>
        Server A uses binary logging with ROW format.
        Server B reads the changes and applies them
        to its replicated database.
    </p>

    <div class="info">
        Server A server-id: 1<br>
        Server B server-id: 2<br>
        Binary logging: Enabled<br>
        Replication format: ROW<br>
        Server B read-only mode: Enabled
    </div>

    <p>
        Website backups and database replication are
        separate processes. Website files are copied
        hourly, while database changes are replicated
        continuously.
    </p>


    <h2>5. Required Test Results</h2>

    <h3>Database Replication Test</h3>

    <p>
        A test visitor count was changed on Server A.
        The updated value was then checked on Server B.
        Both servers showed the same visitor count.
    </p>

    <div class="info">
        <strong>Result:</strong> Successful.<br>
        Slave_IO_Running: Yes<br>
        Slave_SQL_Running: Yes<br>
        Seconds_Behind_Master: 0
    </div>

    <h3>Automatic Backup Test</h3>

    <p>
        The backup script was run manually and automatic
        hourly execution was also confirmed through
        the backup log.
    </p>

    <div class="info">
        <strong>Result:</strong> Successful backups were
        recorded, including the hourly backup at 16:00 UTC
        on 22 November 2026.
    </div>

    <h3>Website Restoration Test</h3>

    <p>
        A backed-up index.html file was copied from
        Server B to a restore-test directory on Server A.
        The original and restored files were compared
        using the diff command.
    </p>

    <div class="info">
        <strong>Result:</strong> The files were identical.
    </div>

    <h3>Week 4 Application Test</h3>

    <p>
        The Flask application on Server B successfully
        read the visitor count from the replicated database.
        The value was checked against the database.
    </p>

    <div class="info">
        <strong>Result:</strong> Successful.
        The read-only visitor counter displayed the
        replicated value.
    </div>


    <h2>6. Problem Solved and What I Learned</h2>

    <p>
        One problem I encountered was that the original
        Week 2 visitor counter stored its value in a local
        text file instead of MariaDB.
    </p>

    <p>
        Because of this, the visitor count in the database
        did not increase when the website counter was used.
        Server B therefore displayed an older value.
    </p>

    <p>
        I solved the problem by changing the Week 2
        application to update the visitor count directly
        in MariaDB.
    </p>

    <p>
        After the change, the database replicated the
        updated value to Server B, and the Week 4 website
        displayed the correct count.
    </p>

    <p>
        I learned how database replication, Linux
        permissions, SSH, rsync and cron work together
        to create a more reliable server setup.
    </p>


    <h2>Conclusion</h2>

    <p>
        The Week 4 project extended the original server
        with a second virtual machine. MariaDB replication
        keeps the database copy updated, while rsync
        creates hourly website backups.
    </p>

    <p>
        The restoration test confirmed that backed-up
        website files could be recovered successfully.
        The read-only visitor counter also demonstrated
        that Server B can use the replicated database
        without modifying it.
    </p>

</main>

<footer>
    <p>Week 4 - Linux Server Administration</p>
    <p>CSC cPouta | Ubuntu | Nginx | Flask | MariaDB</p>
</footer>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001)


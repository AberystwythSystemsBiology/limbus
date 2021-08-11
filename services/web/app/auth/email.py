Delete soon
# Copyright (C) 2019  Keiron O'Shea <keo7@aber.ac.uk>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from flask_mail import Mail, Message

from Flask import Flask

app = Flask(__name__)
app.config.update(
    DEBUG=True,
    #EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME = '3dglprinting@gmail.com',
    MAIL_PASSWORD = 'ilA4lifeathD'
    )
mail = Mail(app)

@auth.route('/sendemail')
def send_mail():
    try:
        msg = Message("Send Mail Tutorial!",
          sender="3dglprinting@gmail.com",
          recipients=["dglwwe98@gmail.com"])
        msg.body = "Yo!\nHave you heard the good word of Python???"           
        mail.send(msg)
        return 'Mail sent!'
    except Exception, e:
        return(str(e)) 


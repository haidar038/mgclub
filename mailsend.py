from mailersend import emails
from dotenv import load_dotenv

load_dotenv()

mailer = emails.NewEmail(os.getenv('MAILERSEND_API_KEY'))

# define an empty dict to populate with mail values
mail_body = {}

mail_from = {
    "name": "Your Name",
    "email": "your@domain.com",
}

recipients = [
    {
        "name": "Your Client",
        "email": "your@client.com",
    }
]


variables = [
    {
        "email": "your@client.com",
        "substitutions": [
            {
                "var": "foo",
                "value": "bar"
            },
        ]
    }
]


mailer.set_mail_from(mail_from, mail_body)
mailer.set_mail_to(recipients, mail_body)
mailer.set_subject("Hello from {$company}", mail_body)
mailer.set_template("templateID", mail_body)
mailer.set_simple_personalization(variables, mail_body)

mailer.send(mail_body)
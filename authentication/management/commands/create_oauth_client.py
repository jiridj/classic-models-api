import secrets

from django.core.management.base import BaseCommand, CommandError

from authentication.models import OAuthClient


class Command(BaseCommand):
    help = (
        "Register a new OAuth 2.0 client. Prints the client_id and client_secret once "
        "— the secret is not recoverable after this point."
    )

    def add_arguments(self, parser):
        parser.add_argument("name", help="Human-readable name for this client (e.g. 'watsonx Orchestrate')")
        parser.add_argument(
            "redirect_uris",
            nargs="+",
            help="One or more allowed redirect URIs for this client",
        )

    def handle(self, *args, **options):
        name = options["name"]
        redirect_uris = options["redirect_uris"]

        if OAuthClient.objects.filter(name=name).exists():
            raise CommandError(
                f"A client named '{name}' already exists. "
                "Use a unique name or delete the existing client first."
            )

        raw_secret = secrets.token_urlsafe(32)

        client = OAuthClient(
            name=name,
            redirect_uris="\n".join(redirect_uris),
        )
        client.set_secret(raw_secret)
        client.save()

        self.stdout.write(self.style.SUCCESS("\nOAuth client registered successfully.\n"))
        self.stdout.write(f"  Name:          {client.name}")
        self.stdout.write(f"  Client ID:     {client.client_id}")
        self.stdout.write(f"  Client Secret: {raw_secret}")
        self.stdout.write(f"  Redirect URIs: {', '.join(redirect_uris)}")
        self.stdout.write(
            self.style.WARNING(
                "\n⚠  The client secret is shown only once and cannot be recovered. "
                "Store it securely now.\n"
            )
        )

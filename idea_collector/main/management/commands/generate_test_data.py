import random

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

from main.models import Item, Tag


WORDS = [
    "alpha", "bravo", "charlie", "delta", "echo", "foxtrot", "golf", "hotel",
    "india", "juliet", "kilo", "lima", "mike", "november", "oscar", "papa",
    "quebec", "romeo", "sierra", "tango", "uniform", "victor", "whiskey",
    "xray", "yankee", "zulu", "drum", "factory", "sample", "loop", "beat",
    "sound", "audio", "video", "image", "record", "track", "session", "studio",
    "mix", "master", "project", "idea", "concept", "design", "draft", "note",
    "demo", "version", "release", "archive", "folder", "file", "catalog",
]

TAG_NAMES = [
    "music", "drums", "beats", "samples", "loops", "synth", "bass", "guitar",
    "vocals", "mixing", "mastering", "recording", "studio", "live", "acoustic",
    "electronic", "hiphop", "rock", "jazz", "classical",
]

COLOR_VALUES = ["#0d6efd", "#6c757d", "#198754", "#dc3545", "#ffc107", "#0dcaf0", "#fe04c8"]


def random_text(min_words, max_words):
    count = random.randint(min_words, max_words)
    return " ".join(random.choice(WORDS) for _ in range(count))


def random_html():
    paragraphs = [
        f"<p>{random_text(15, 40)}</p>" for _ in range(random.randint(1, 4))
    ]
    return "".join(paragraphs)


class Command(BaseCommand):
    help = "Generate random tags and items for performance testing."

    def add_arguments(self, parser):
        parser.add_argument("--items", type=int, help="Number of items to create.")
        parser.add_argument("--tags", type=int, help="Number of tags to create.")
        parser.add_argument("--flush", action="store_true", help="Delete all items and tags and exit.")

    def handle(self, *args, **options):
        item_count = options["items"]
        tag_count = options["tags"]

        if options["flush"]:
            Item.objects.all().delete()
            Tag.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("Database emptied: all items and tags deleted."))
            return

        if item_count is None or tag_count is None:
            raise CommandError("Both --items and --tags are required.")

        tag_pool = list(TAG_NAMES[:tag_count])
        if len(tag_pool) < tag_count:
            tag_pool += [f"tag-{i}" for i in range(len(tag_pool), tag_count)]

        tags = []
        for name in tag_pool:
            tag, _ = Tag.objects.get_or_create(
                name=name,
                defaults={"color": random.choice(COLOR_VALUES)},
            )
            tags.append(tag)
        self.stdout.write(self.style.SUCCESS(f"{len(tags)} tags available."))

        for i in range(item_count):
            item = Item.objects.create(
                name=f"{random_text(1, 3).title()} {i + 1}",
                description=random_html(),
                color=random.choice([c[0] for c in Item.COLOR_CHOICES]),
            )
            item.tags.set(random.sample(tags, k=random.randint(1, min(5, len(tags)))))

        self.stdout.write(self.style.SUCCESS(f"{item_count} items created."))

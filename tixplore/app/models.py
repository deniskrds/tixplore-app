from tortoise import Model, fields


class Base(Model):
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    is_active = fields.BooleanField(default=True)

    class Meta:
        abstract = True


class Users(Base):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255)
    password = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)

    class Meta:
        table = "users"


class TicketSites(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)
    price = fields.FloatField()
    url = fields.CharField(max_length=255)
    event = fields.ForeignKeyField("models.Events", related_name="ticket_sites")

    class Meta:
        table = "ticket_sites"


class Events(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    type = fields.CharField(max_length=100)
    genre = fields.CharField(max_length=300)
    location = fields.CharField(max_length=255)
    time = fields.CharField(max_length=40)
    image_url = fields.CharField(max_length=255, null=True)
    description = fields.TextField()
    director = fields.CharField(max_length=100)
    cast = fields.JSONField()  # Storing list of actors as JSON
    duration = fields.CharField(max_length=50)
    rating = fields.FloatField()
    favorite = fields.BooleanField(default=False)

    class Meta:
        table = "events"

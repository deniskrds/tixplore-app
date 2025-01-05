TORTOISE_ORM = {
    "connections": {
        "default": "postgres://postgres@localhost:5432/tixplore"
    },
    "apps": {
        "models": {
            "models": ["app.models", "aerich.models"],
            "default_connection": "default",
        },
    },
}

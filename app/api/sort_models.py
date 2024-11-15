from fuzzywuzzy import fuzz


def correction_function(views):
    return (views ** 0.5) / (views ** 0.5 + 20)


def sort_by_popularity(data, settings):
    return data.rang + correction_function(data.count_views)


def sort_by_likeness(data, settings):
    return fuzz.ratio(data.name, settings.search) + sort_by_popularity(data, settings) / 100


def sort_by_views(data, settings):
    return data.count_views


def sort_by_rating(data, settings):
    return data.average_rating + correction_function(data.count_views) / 10


def sort_by_name(data, settings):
    return data.username.lower() + ' ' + data.name.lower()


def sort_by_publication(data, settings):
    return data.date_creation


def sort_by_last_update(data, settings):
    return data.latest_update

import scraper
import pandas as pd

def get_contextuals(name, country=None, entity_type=None, get_lat_lng=True, source=True):
    """
    Given a name, country, and entity_type, pulls contextual information from
    an appropriate data source.
    """

    def can_float(x):
        try:
            float(x)
            return True
        except:
            return False

    def update_with_source(data, new):
        if new is None:
            return data

        for key, value in new.items():
            if key != 'source_url' or not source:
                data[key] = value
                if source:
                    data[key + '_source'] = new['source_url']
        return data

    ctx = {}

    if entity_type in ['City', 'Region', 'Municipality', 'Town', 'University', 'Higher Education', 'Education']:

        wiki = scraper.contextuals.wikipedia.get_data(name, country, entity_type)
        ctx = update_with_source(ctx, wiki)

    else:

        bloomberg = scraper.contextuals.bloomberg.get_data(name, country, entity_type)
        ctx = update_with_source(ctx, bloomberg)

        # if revenue is None,
        if 'revenue' not in ctx or ctx['revenue'] is None:

            if ctx is None: ctx = {}

            # try Hoovers.
            h = scraper.contextuals.hoovers.get_data(name, country, entity_type)
            ctx = update_with_source(ctx, h)

    # if we should get lat/lng and lat or lng aren't floats,
    if get_lat_lng and (('lat' not in ctx or not can_float(ctx['lat'])) or ('lng' not in ctx or not can_float(ctx['lng']))):
        # if headquarters isn't None
        if 'headquarters' in ctx and ctx['headquarters'] is not None:
            # try the google geocoder on the headquarters address.
            ctx['lat'], ctx['lng'], _ = scraper.contextuals.geocode(ctx['headquarters'])
        else:
            # otherwise try the Google geocoder on the name.
            ctx['lat'], ctx['lng'], _ = scraper.contextuals.geocode(name + ', ' + country)

        ctx['lat_source'] = 'Google Geocoder'
        ctx['lng_source'] = 'Google Geocoder'

    return ctx

def get_possible_names(name, country=None, entity_type=None):
    """
    Given a name, country, and entity type (all of which can be left as None)
    returns the titles of pages that redirect to the resolved wikipedia page.
    """
    p = scraper.contextuals.wikipedia.resolve_page(name, country, entity_type)['page']
    return p.redirects

def get_country(name, entity_type=None):
    """
    Given a name and an entity type,
    returns the matching country based on a wikipedia search
    """
    p = scraper.contextuals.wikipedia.resolve_page(name, None, entity_type)['page']
    c = scraper.contextuals.wikipedia.infer_country(p)
    return c

def get_entity_type(name, country=None):
    """
    Given a country and a name,
    returns the matching entity type based on a wikipedia search
    """
    p = scraper.contextuals.wikipedia.resolve_page(name, country, None)['page']
    t = scraper.contextuals.wikipedia.infer_type(p)
    return t

def gapfill(df):
    out = []

    for n,row in df.iterrows():
        row = dict(row)
        try:
            ctx = get_contextuals(row['name'], row['iso'], row['entity_type'])
        except Exception as e:
            print(e)

        ctx = None
        if ctx is not None:
            # fill in ctx with keys from row.
            ctx.update(row)
        else:
            ctx = row
        out.append(ctx)

    return pd.DataFrame(out)

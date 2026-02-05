from django import template

register = template.Library()


@register.filter
def unique_insights(insights):
    """Return a list of insights deduplicated by normalized title.

    Keeps the latest `created_at` per unique title and returns a list
    sorted by `created_at` descending.
    """
    if not insights:
        return []

    seen = {}
    for ins in insights:
        try:
            key = (ins.title or '').strip().lower()
        except Exception:
            key = str(ins)

        if not key:
            # fallback to object id/repr
            key = f"__ins__{getattr(ins, 'id', id(ins))}"

        existing = seen.get(key)
        if existing is None:
            seen[key] = ins
        else:
            # keep the latest by created_at when possible
            try:
                if getattr(ins, 'created_at', None) and getattr(existing, 'created_at', None):
                    if ins.created_at > existing.created_at:
                        seen[key] = ins
            except Exception:
                # if comparison fails, keep existing
                pass

    # sort by created_at desc if available
    def _sort_key(i):
        return getattr(i, 'created_at', None) or 0

    return sorted(seen.values(), key=_sort_key, reverse=True)

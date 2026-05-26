from ebook.cache_utils import bump_namespace_version


PHYSICAL_MATERIAL_CACHE_NAMESPACE = "materials:physical"
DIGITAL_MATERIAL_CACHE_NAMESPACE = "materials:digital"
MATERIAL_INTERACTION_CACHE_NAMESPACE = "materials:interactions"
MATERIAL_FEEDBACK_CACHE_NAMESPACE = "materials:feedback"
MATERIAL_LOOKUP_CACHE_NAMESPACE = "materials:lookup:v4"
LIBRARY_CACHE_NAMESPACE = "libraries:read"


def invalidate_material_caches():
    for namespace in (
        PHYSICAL_MATERIAL_CACHE_NAMESPACE,
        DIGITAL_MATERIAL_CACHE_NAMESPACE,
        MATERIAL_INTERACTION_CACHE_NAMESPACE,
        MATERIAL_FEEDBACK_CACHE_NAMESPACE,
        MATERIAL_LOOKUP_CACHE_NAMESPACE,
    ):
        bump_namespace_version(namespace)


def invalidate_library_caches():
    bump_namespace_version(LIBRARY_CACHE_NAMESPACE)

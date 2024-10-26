def register():
    from . import workflows
    workflows.register()


def unregister():
    from . import workflows
    workflows.unregister()

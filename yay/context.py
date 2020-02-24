import os

from yay import YayException
from yay.util import read_yaml_file

#
# Yay-context.yaml
#

def get_context(script_dir, profile_name):
    context_file = os.path.join(script_dir, 'yay-context.yaml')
    if not os.path.isfile(context_file):
        return {}

    context = read_yaml_file(context_file)[0]
    apply_profile(context, profile_name)

    return context


def apply_profile(context, profile_name):
    profiles = context.pop('profiles', None)
    if profile_name:
        if profiles and profile_name in profiles:
            dict_merge(context, profiles[profile_name])
        else:
            raise YayException(f"Profile '{profile_name}' not found in yay-context.yaml")


def dict_merge(context, profile):
    for key in profile:
        if key in context:
            context[key].update(profile[key])
        else:
            context[key] = profile[key]
import attr


@attr.s
class ComparedPage:
    Jahia_url = attr.ib(default='', validator=attr.validators.instance_of(str))
    Jahia_username = attr.ib(default='', validator=attr.validators.instance_of(str))
    Jahia_password = attr.ib(default='', validator=attr.validators.instance_of(str))
    Jahia_screenshot_file = attr.ib(default='', validator=attr.validators.instance_of(str))
    Jahia_screenshot_highlighted_file = attr.ib(default='', validator=attr.validators.instance_of(str))

    WP_url = attr.ib(default='', validator=attr.validators.instance_of(str))
    WP_username = attr.ib(default='', validator=attr.validators.instance_of(str))
    WP_password = attr.ib(default='', validator=attr.validators.instance_of(str))
    WP_screenshot_file = attr.ib(default='', validator=attr.validators.instance_of(str))
    WP_screenshot_highlighted_file = attr.ib(default='', validator=attr.validators.instance_of(str))

    SSIM_score = attr.ib(default=0.0, validator=attr.validators.instance_of(float))

    Persons_in_charge = attr.ib(default=[], validator=attr.validators.instance_of(list))


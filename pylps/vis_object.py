import copy


def pylps_vis_meta(cls_name, cls_parents, cls_attrs):
    print(cls_name)

    modified_cls_attrs = copy.deepcopy(cls_attrs)

    # Set class name
    modified_cls_attrs['name'] = cls_name

    return type(cls_name, cls_parents, modified_cls_attrs)


class PylpsVisObject(object):

    def __repr__(self):
        ret = "VIS OBJ %s | " % (self.name)
        ret += "Args: %s\n" % str(self.stored_args)
        return ret

from connexion.resolver import Resolver, Resolution


class CustomOperationResolverException(Exception):
    pass


class CustomOperationResolver(Resolver):
    """
    Resolves endpoint functions using Dictionary: <path,function>
    """

    def __init__(self, functions_dictionary):
        Resolver.__init__(self)
        self.functions_dictionary = functions_dictionary

    def resolve(self, operation):
        if operation.path not in self.functions_dictionary:
            raise CustomOperationResolverException(
                "Missing mapping for path: ", operation.path
            )
        return Resolution(
            self.functions_dictionary[operation.path], operation.path.replace("/", "__")
        )

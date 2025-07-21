import itds


class MaxFileSizeReachedError(itds.ValidationError):
	pass


class FolderNotEmpty(itds.ValidationError):
	pass


class FileTypeNotAllowed(itds.ValidationError):
	pass


from itds.exceptions import *

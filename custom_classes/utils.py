import re

def get_identity(ctx):
	r = re.compile(r'[a-z A-Z-]*\, [a-z A-Z-]*\|\d{1,}')
	identity = [r.match(role.name).string
     			for role in ctx.author.roles 
				if r.match(role.name)]
	return identity


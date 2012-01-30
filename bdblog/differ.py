from re import sub
from diff_match_patch import diff_match_patch as Differ
differ = Differ()


def diff(text1, text2):
	diff = differ.diff_main(text2, text1)
	differ.diff_cleanupSemantic(diff)
	return differ.diff_toDelta(diff)

def patch(text2, delta):
	diff = differ.diff_fromDelta(text2, delta)
	patch = differ.patch_make(diff)
	return differ.patch_apply(patch, text2)[0]

def diff_to_html(text2, delta):
	diff = differ.diff_fromDelta(text2, delta)
	html = differ.diff_prettyHtml(diff)
	return sub("&para;<br>", "<br />", html)

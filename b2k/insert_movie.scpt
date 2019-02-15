on run argv

	-- Get Keynote file name. --
	set key_file to item 1 of argv
	set key_file to POSIX file key_file as string

	-- Get movie file name. --
	set mov_file to item 2 of argv
	set mov_file to POSIX file mov_file as string

	-- Get slide number. --
	set slide_number to item 3 of argv as integer

	-- Get movie size. --
	-- set mov_width  to item 4 of argv as integer
	-- set mov_height to item 5 of argv as integer

	tell application "Keynote"
		activate
		close every document without saving

		set thisDocument to open alias key_file

		tell thisDocument

			-- Get document size. --
			set docWidth to the width
			set docHeight to the height

			tell the slide slide_number
				set thisMovie to make new image with properties {file:alias mov_file}
				tell thisMovie
					set position to {(docWidth - width) div 2, (docHeight - height) div 2}
					set repetition method to loop
				end tell

			end tell -- End slide. --

		end tell -- End document. --

		save thisDocument
		close every document without saving
		quit saving no

	end tell -- End Keynote. --

end run
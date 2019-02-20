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

			set movWidth to Â
			(do shell script "mdls -raw -name kMDItemPixelWidth " & Â
				quoted form of POSIX path of mov_file) as integer
			set movHeight to Â
			(do shell script "mdls -raw -name kMDItemPixelHeight " & Â
				quoted form of POSIX path of mov_file) as integer

			set ratioWidth to the (movWidth/docWidth)
			set ratioHeight to the (movHeight/(docHeight*0.8))
			if ratioWidth is greater than or equal to ratioHeight then
				set newMovWidth to the (movWidth/ratioWidth)
				set newMovHeight to the (movHeight/ratioWidth)
			else
				set newMovWidth to the (movWidth/ratioHeight)
				set newMovHeight to the (movHeight/ratioHeight)
			end if

			tell the slide slide_number
				set thisMovie to make new image with properties {file:alias mov_file, width:newMovWidth, height:newMovHeight}
				tell thisMovie
					set position to {(docWidth - width) div 2, (((docHeight - 105) - height) div 2) + 80}
					set repetition method to loop
				end tell

			end tell -- End slide. --

		end tell -- End document. --

		save thisDocument
		close every document without saving
		quit saving no

	end tell -- End Keynote. --

end run
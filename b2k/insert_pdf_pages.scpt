on run argv

	-- Define directory containing all pdf pages. --
	set POSIX_path to item 1 of argv
	set SCPT_path to POSIX file POSIX_path as string

	-- Retrieve all pdf pages in file_list. --
	tell application "Finder"
    set file_list to name of every file of entire contents of alias SCPT_path
  end tell

	-- Get file_list size. --
	set file_list_size to count of file_list

	-- Create Keynote presentation. --
	tell application "Keynote"
		activate
		close every document without saving

		-- Set white theme. --
		set installedThemes to name of every theme
		set localTheme to item 2 of installedThemes
		set thisDocument to make new document with properties {document theme:theme localTheme}


		tell thisDocument

			-- Get document size. --
			set docWidth to the width
			set docHeight to the height

			-- Insert all pdf pages. --
			repeat with pdf_page in file_list
				set current_file to SCPT_path & ":" & pdf_page
				tell the current slide
					set newImageItem to make new image with properties {file:alias current_file}
					tell newImageItem
						set position to {0, 0}
						set width to docWidth
						set height to docHeight
					end tell
				end tell
				make new slide
			end repeat
			delete slide (file_list_size + 1 as integer)

		end tell -- End document. --

		-- Save the document. --
		set export_file to SCPT_path & ":..:main.key"
		save thisDocument in file export_file
		close every document without saving
		quit saving no

	end tell -- End application Keynote. --
end run -- End run argv. --

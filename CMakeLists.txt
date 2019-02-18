project(beamer_template NONE)
cmake_minimum_required(VERSION 3.2)
find_package(PythonInterp)
include(UseLATEX.cmake)

file(GLOB_RECURSE CONTENTS_FILES RELATIVE ${CMAKE_SOURCE_DIR} src/*.tex)

add_latex_document(main.tex
                   TARGET_NAME
                   ${CMAKE_PROJECT_NAME}
                   INPUTS
                   ${CONTENTS_FILES}
                   src/config/custom-numeric-comp.bbx
                   IMAGE_DIRS
                   fig
                   src/config/logos
                   BIBFILES
                   src/biblio.bib
                   USE_BIBLATEX)

add_custom_command(TARGET pdf POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy main.pdf
                           ${CMAKE_PROJECT_NAME}.pdf
                   COMMENT "Copying main.pdf to ${CMAKE_PROJECT_NAME}.pdf")

set(EXTRACT_KEY extract_key)
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/${EXTRACT_KEY})
add_custom_target(key DEPENDS ${CMAKE_SOURCE_DIR}/b2k/* main.key)
add_custom_command(OUTPUT main.key
                   DEPENDS ${CMAKE_SOURCE_DIR}/b2k/* main.pdf
                   COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/b2k/* .
                   COMMAND ${PYTHON_EXECUTABLE} beamer2keynote.py
                           --in ${CMAKE_BINARY_DIR}/main.pdf
                           --tmp-dir ${CMAKE_BINARY_DIR}/${EXTRACT_KEY}
                           --src-dir ${CMAKE_SOURCE_DIR}
                   COMMAND ${CMAKE_COMMAND} -E copy main.key
                           ${CMAKE_PROJECT_NAME}.key
                   COMMENT "Converting main.pdf to ${CMAKE_PROJECT_NAME}.key")

set(EXTRACT_HTML extract_html)
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/${EXTRACT_HTML})
add_custom_target(remark_html DEPENDS ${CMAKE_SOURCE_DIR}/b2html/* remark.html)
add_custom_command(OUTPUT remark.html
                   DEPENDS ${CMAKE_SOURCE_DIR}/b2html/* main.pdf
                   COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_SOURCE_DIR}/b2html/*
                           .
                   COMMAND ${PYTHON_EXECUTABLE} beamer2html.py
                           --in ${CMAKE_BINARY_DIR}/main.pdf
                           --tmp-dir ${CMAKE_BINARY_DIR}/${EXTRACT_HTML}
                           --src-dir ${CMAKE_SOURCE_DIR}
                           --assets-dir html_slides_${CMAKE_PROJECT_NAME}
                   COMMAND ${CMAKE_COMMAND} -E copy remark.html
                           ${CMAKE_PROJECT_NAME}.html
                   COMMENT "Converting main.pdf to ${CMAKE_PROJECT_NAME}.html")

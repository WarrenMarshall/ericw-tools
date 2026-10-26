set(QBSP_INCLUDES
	../include/qbsp/qbsp.hh
	../include/qbsp/brush.hh
	../include/qbsp/csg.hh
	../include/qbsp/exportobj.hh
	../include/qbsp/map.hh
	../include/qbsp/winding.hh
	../include/qbsp/merge.hh
	../include/qbsp/outside.hh
	../include/qbsp/portals.hh
	../include/qbsp/prtfile.hh
	../include/qbsp/brushbsp.hh
	../include/qbsp/faces.hh
	../include/qbsp/tjunc.hh
	../include/qbsp/tree.hh
	../include/qbsp/writebsp.hh)

set(QBSP_SOURCES
	brush.cc
	csg.cc
	map.cc
	merge.cc
	outside.cc
	portals.cc
	prtfile.cc
	qbsp.cc
	brushbsp.cc
	faces.cc
	tjunc.cc
	tree.cc
	writebsp.cc
	exportobj.cc
	${QBSP_INCLUDES})

add_library(libqbsp STATIC ${QBSP_SOURCES})
target_link_libraries(libqbsp common ${CMAKE_THREAD_LIBS_INIT} TBB::tbb TBB::tbbmalloc fmt::fmt nlohmann_json::nlohmann_json pareto)

# Both frontends share one compiler implementation. The qbsp target is retained
# for upstream tooling; it also contains downstream corrections on this branch.
execute_process(COMMAND git rev-parse HEAD WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    OUTPUT_VARIABLE QQBSP_REVISION OUTPUT_STRIP_TRAILING_WHITESPACE)
execute_process(COMMAND git status --porcelain --untracked-files=no WORKING_DIRECTORY ${PROJECT_SOURCE_DIR}
    OUTPUT_VARIABLE QQBSP_DIRTY OUTPUT_STRIP_TRAILING_WHITESPACE)
if(QQBSP_DIRTY)
    string(APPEND QQBSP_REVISION "-dirty")
endif()
if(NOT QQBSP_REVISION)
    message(FATAL_ERROR "qqbsp identity requires a Git checkout")
endif()
add_executable(qqbsp main.cc)
target_compile_definitions(qqbsp PRIVATE
    QQBSP_BUILD_ID="Qartographer qqbsp; upstream=ccaeb8457a1267860ebe99ed1df7394ebdd6b435; downstream=${QQBSP_REVISION}; patches=P1")
add_executable(qbsp main.cc)
foreach(compiler IN ITEMS qqbsp qbsp)
    target_link_libraries(${compiler} libqbsp)
    install(TARGETS ${compiler} RUNTIME DESTINATION .)
    add_custom_command(TARGET ${compiler} POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_FILE:TBB::tbb>" "$<TARGET_FILE_DIR:${compiler}>"
        COMMAND ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_FILE:TBB::tbbmalloc>" "$<TARGET_FILE_DIR:${compiler}>")
    copy_mingw_dlls(${compiler})
    add_loader_path_to_rpath(${compiler})
endforeach()

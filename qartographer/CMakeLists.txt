# QBSP-only upstream tests. Never link liblight/libvis or build their suites.
file(COPY ${PROJECT_SOURCE_DIR}/testmaps/ DESTINATION ${CMAKE_CURRENT_BINARY_DIR}/upstream-testmaps)
file(WRITE ${CMAKE_CURRENT_BINARY_DIR}/testmaps.hh
    "inline const char *testmaps_dir = \"${CMAKE_CURRENT_BINARY_DIR}/upstream-testmaps\";\ninline const char *test_quake_maps_dir = \"\";\ninline const char *test_quake2_maps_dir = \"\";\ninline const char *test_hexen2_maps_dir = \"\";\ninline const char *test_halflife_maps_dir = \"\";\n")
add_executable(qqbsp_tests ../tests/test_qbsp.cc ../tests/test_main.cc)
target_include_directories(qqbsp_tests PRIVATE ${CMAKE_CURRENT_BINARY_DIR})
target_link_libraries(qqbsp_tests libqbsp GTest::gtest GTest::gmock)
add_custom_command(TARGET qqbsp_tests POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_FILE:TBB::tbb>" "$<TARGET_FILE_DIR:qqbsp_tests>"
    COMMAND ${CMAKE_COMMAND} -E copy_if_different "$<TARGET_FILE:TBB::tbbmalloc>" "$<TARGET_FILE_DIR:qqbsp_tests>")
copy_mingw_dlls(qqbsp_tests)
add_loader_path_to_rpath(qqbsp_tests)

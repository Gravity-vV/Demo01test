## deepseek_silicon 0x0000000020e0a4bc775eb0cbefc7cfbeafc88444 (51685599-94c7-4a9d-bb42-e08bb6f89510)
- start_line: 55
- a1_timeout: False, a2_timeout: True, retry_count: 1
- key_events:
  - L55 [start] 2026-03-02 21:25:46,046 - src.workflow.engine - INFO - Starting workflow for session 51685599-94c7-4a9d-bb42-e08bb6f89510 with model: deepseek_silicon
  - L58 [node1] 2026-03-02 21:25:47,113 - src.workflow.engine - INFO - Executing node 1/5: 1728096797608 (llm) with model deepseek_silicon
  - L89 [node2] 2026-03-02 21:26:36,382 - src.workflow.engine - INFO - Executing node 2/5: 1728113785964 (llm) with model deepseek_silicon
  - L116 [retry_node2] 2026-03-02 21:27:36,385 - openai._base_client - INFO - Retrying request to /chat/completions in 0.441062 seconds
  - L118 [timeout_node2] ⏰ Deepseek_Silicon API call timed out after 60 seconds
  - L119 [timeout_node2] 💥 All AI models failed. Last error: Deepseek_Silicon API call timed out after 60 seconds
  - L120 [timeout_node2] 2026-03-02 21:27:41,388 - src.workflow.nodes - ERROR - Audit plan creation failed: All AI models failed. Last error: Deepseek_Silicon API call timed out after 60 seconds
  - L125 [node3] 2026-03-02 21:27:41,389 - src.workflow.engine - INFO - Executing node 3/5: 1728114018925 (parameter-extractor) with model deepseek_silicon
  - L133 [node4] 2026-03-02 21:27:41,389 - src.workflow.engine - INFO - Executing node 4/5: 1728114855021 (iteration) with model deepseek_silicon
  - L145 [node5] 2026-03-02 21:27:45,843 - src.workflow.engine - INFO - Executing node 5/5: 1728120734743 (llm) with model deepseek_silicon

## deepseek_silicon 0x000000e45ffaab3552f1eba4b2799b6803322c12 (a55b2d79-0b3a-4194-a135-1f71b96fb21f)
- start_line: 199
- a1_timeout: False, a2_timeout: False, retry_count: 2
- key_events:
  - L199 [start] 2026-03-02 21:28:18,720 - src.workflow.engine - INFO - Starting workflow for session a55b2d79-0b3a-4194-a135-1f71b96fb21f with model: deepseek_silicon
  - L205 [node1] 2026-03-02 21:28:22,175 - src.workflow.engine - INFO - Executing node 1/5: 1728096797608 (llm) with model deepseek_silicon
  - L237 [node2] 2026-03-02 21:29:10,968 - src.workflow.engine - INFO - Executing node 2/5: 1728113785964 (llm) with model deepseek_silicon
  - L264 [node3] 2026-03-02 21:29:51,679 - src.workflow.engine - INFO - Executing node 3/5: 1728114018925 (parameter-extractor) with model deepseek_silicon
  - L272 [node4] 2026-03-02 21:29:51,679 - src.workflow.engine - INFO - Executing node 4/5: 1728114855021 (iteration) with model deepseek_silicon
  - L447 [retry_node4] 2026-03-02 21:36:04,229 - openai._base_client - INFO - Retrying request to /chat/completions in 0.497229 seconds
  - L459 [timeout_node4] ⏰ Deepseek_Silicon API call timed out after 60 seconds
  - L460 [timeout_node4] 💥 All AI models failed. Last error: Deepseek_Silicon API call timed out after 60 seconds
  - L502 [retry_node4] 2026-03-02 21:39:42,880 - openai._base_client - INFO - Retrying request to /chat/completions in 0.489104 seconds
  - L510 [timeout_node4] ⏰ Deepseek_Silicon API call timed out after 60 seconds
  - L511 [timeout_node4] 💥 All AI models failed. Last error: Deepseek_Silicon API call timed out after 60 seconds
  - L539 [node5] 2026-03-02 21:40:48,237 - src.workflow.engine - INFO - Executing node 5/5: 1728120734743 (llm) with model deepseek_silicon

## deepseek_silicon 0x000ee2ed96e1d1277a67864dedd42140dcc6b835 (5d515fc1-52a8-4d3a-b036-1d0d6422ab89)
- start_line: 592
- a1_timeout: True, a2_timeout: False, retry_count: 1
- key_events:
  - L592 [start] 2026-03-02 21:41:34,017 - src.workflow.engine - INFO - Starting workflow for session 5d515fc1-52a8-4d3a-b036-1d0d6422ab89 with model: deepseek_silicon
  - L596 [node1] 2026-03-02 21:41:35,025 - src.workflow.engine - INFO - Executing node 1/5: 1728096797608 (llm) with model deepseek_silicon
  - L617 [retry_node1] 2026-03-02 21:43:55,175 - openai._base_client - INFO - Retrying request to /chat/completions in 0.386479 seconds
  - L625 [timeout_node1] ⏰ Deepseek_Silicon API call timed out after 60 seconds
  - L626 [timeout_node1] 💥 All AI models failed. Last error: Deepseek_Silicon API call timed out after 60 seconds
  - L627 [timeout_node1] 2026-03-02 21:44:19,050 - src.workflow.nodes - ERROR - Initial analysis failed: All AI models failed. Last error: Deepseek_Silicon API call timed out after 60 seconds
  - L632 [node2] 2026-03-02 21:44:19,051 - src.workflow.engine - INFO - Executing node 2/5: 1728113785964 (llm) with model deepseek_silicon
  - L660 [node3] 2026-03-02 21:44:54,309 - src.workflow.engine - INFO - Executing node 3/5: 1728114018925 (parameter-extractor) with model deepseek_silicon
  - L668 [node4] 2026-03-02 21:44:54,309 - src.workflow.engine - INFO - Executing node 4/5: 1728114855021 (iteration) with model deepseek_silicon
  - L899 [node5] 2026-03-02 21:52:26,241 - src.workflow.engine - INFO - Executing node 5/5: 1728120734743 (llm) with model deepseek_silicon

## deepseek_school 0x0000000020e0a4bc775eb0cbefc7cfbeafc88444 (88bb3104-ae5e-4348-bc03-fa744855434b)
- start_line: 959
- a1_timeout: True, a2_timeout: True, retry_count: 3
- key_events:
  - L959 [start] 2026-03-02 21:56:07,220 - src.workflow.engine - INFO - Starting workflow for session 88bb3104-ae5e-4348-bc03-fa744855434b with model: deepseek_school
  - L963 [node1] 2026-03-02 21:56:08,212 - src.workflow.engine - INFO - Executing node 1/5: 1728096797608 (llm) with model deepseek_school
  - L990 [retry_node1] 2026-03-02 21:57:08,274 - openai._base_client - INFO - Retrying request to /chat/completions in 0.402124 seconds
  - L992 [timeout_node1] ⏰ Deepseek_School API call timed out after 60 seconds
  - L993 [timeout_node1] 💥 All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L994 [timeout_node1] 2026-03-02 21:57:13,218 - src.workflow.nodes - ERROR - Initial analysis failed: All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L999 [node2] 2026-03-02 21:57:13,219 - src.workflow.engine - INFO - Executing node 2/5: 1728113785964 (llm) with model deepseek_school
  - L1025 [retry_node2] 2026-03-02 21:58:08,748 - openai._base_client - INFO - Retrying request to /chat/completions in 0.859786 seconds
  - L1027 [retry_node2] 2026-03-02 21:58:13,277 - openai._base_client - INFO - Retrying request to /chat/completions in 0.416493 seconds
  - L1030 [timeout_node2] ⏰ Deepseek_School API call timed out after 60 seconds
  - L1031 [timeout_node2] 💥 All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L1032 [timeout_node2] 2026-03-02 21:58:18,225 - src.workflow.nodes - ERROR - Audit plan creation failed: All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L1037 [node3] 2026-03-02 21:58:18,225 - src.workflow.engine - INFO - Executing node 3/5: 1728114018925 (parameter-extractor) with model deepseek_school
  - L1045 [node4] 2026-03-02 21:58:18,226 - src.workflow.engine - INFO - Executing node 4/5: 1728114855021 (iteration) with model deepseek_school
  - L1054 [node5] 2026-03-02 21:58:18,226 - src.workflow.engine - INFO - Executing node 5/5: 1728120734743 (llm) with model deepseek_school

## deepseek_school 0x000000e45ffaab3552f1eba4b2799b6803322c12 (d85f8acd-5bd4-4f93-a4ff-1b41c5d18a4a)
- start_line: 1110
- a1_timeout: False, a2_timeout: True, retry_count: 5
- key_events:
  - L1110 [start] 2026-03-02 21:59:13,165 - src.workflow.engine - INFO - Starting workflow for session d85f8acd-5bd4-4f93-a4ff-1b41c5d18a4a with model: deepseek_school
  - L1113 [retry_nodeNone] 2026-03-02 21:59:13,789 - openai._base_client - INFO - Retrying request to /chat/completions in 0.892461 seconds
  - L1117 [node1] 2026-03-02 21:59:16,195 - src.workflow.engine - INFO - Executing node 1/5: 1728096797608 (llm) with model deepseek_school
  - L1141 [retry_node1] 2026-03-02 22:00:09,740 - openai._base_client - INFO - Retrying request to /chat/completions in 0.402309 seconds
  - L1152 [node2] 2026-03-02 22:00:14,697 - src.workflow.engine - INFO - Executing node 2/5: 1728113785964 (llm) with model deepseek_school
  - L1177 [retry_node2] 2026-03-02 22:01:10,226 - openai._base_client - INFO - Retrying request to /chat/completions in 0.947215 seconds
  - L1180 [retry_node2] 2026-03-02 22:01:14,701 - openai._base_client - INFO - Retrying request to /chat/completions in 0.446539 seconds
  - L1181 [retry_node2] 2026-03-02 22:01:14,760 - openai._base_client - INFO - Retrying request to /chat/completions in 0.428298 seconds
  - L1184 [timeout_node2] ⏰ Deepseek_School API call timed out after 60 seconds
  - L1185 [timeout_node2] 💥 All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L1186 [timeout_node2] 2026-03-02 22:01:19,703 - src.workflow.nodes - ERROR - Audit plan creation failed: All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L1191 [node3] 2026-03-02 22:01:19,703 - src.workflow.engine - INFO - Executing node 3/5: 1728114018925 (parameter-extractor) with model deepseek_school
  - L1199 [node4] 2026-03-02 22:01:19,703 - src.workflow.engine - INFO - Executing node 4/5: 1728114855021 (iteration) with model deepseek_school
  - L1208 [node5] 2026-03-02 22:01:19,703 - src.workflow.engine - INFO - Executing node 5/5: 1728120734743 (llm) with model deepseek_school

## deepseek_school 0x000ee2ed96e1d1277a67864dedd42140dcc6b835 (ac7609dc-61f6-44e2-8464-8396b589174f)
- start_line: 1242
- a1_timeout: True, a2_timeout: True, retry_count: 5
- key_events:
  - L1242 [start] 2026-03-02 22:01:22,452 - src.workflow.engine - INFO - Starting workflow for session ac7609dc-61f6-44e2-8464-8396b589174f with model: deepseek_school
  - L1246 [node1] 2026-03-02 22:01:23,285 - src.workflow.engine - INFO - Executing node 1/5: 1728096797608 (llm) with model deepseek_school
  - L1271 [retry_node1] 2026-03-02 22:02:15,217 - openai._base_client - INFO - Retrying request to /chat/completions in 0.757734 seconds
  - L1272 [retry_node1] 2026-03-02 22:02:15,233 - openai._base_client - INFO - Retrying request to /chat/completions in 0.881976 seconds
  - L1276 [retry_node1] 2026-03-02 22:02:23,290 - openai._base_client - INFO - Retrying request to /chat/completions in 0.380112 seconds
  - L1278 [timeout_node1] ⏰ Deepseek_School API call timed out after 60 seconds
  - L1279 [timeout_node1] 💥 All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L1280 [timeout_node1] 2026-03-02 22:02:28,292 - src.workflow.nodes - ERROR - Initial analysis failed: All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L1285 [node2] 2026-03-02 22:02:28,292 - src.workflow.engine - INFO - Executing node 2/5: 1728113785964 (llm) with model deepseek_school
  - L1313 [retry_node2] 2026-03-02 22:03:23,712 - openai._base_client - INFO - Retrying request to /chat/completions in 0.751962 seconds
  - L1315 [retry_node2] 2026-03-02 22:03:28,362 - openai._base_client - INFO - Retrying request to /chat/completions in 0.435811 seconds
  - L1318 [timeout_node2] ⏰ Deepseek_School API call timed out after 60 seconds
  - L1319 [timeout_node2] 💥 All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L1320 [timeout_node2] 2026-03-02 22:03:33,296 - src.workflow.nodes - ERROR - Audit plan creation failed: All AI models failed. Last error: Deepseek_School API call timed out after 60 seconds
  - L1325 [node3] 2026-03-02 22:03:33,296 - src.workflow.engine - INFO - Executing node 3/5: 1728114018925 (parameter-extractor) with model deepseek_school
  - L1333 [node4] 2026-03-02 22:03:33,297 - src.workflow.engine - INFO - Executing node 4/5: 1728114855021 (iteration) with model deepseek_school
  - L1342 [node5] 2026-03-02 22:03:33,297 - src.workflow.engine - INFO - Executing node 5/5: 1728120734743 (llm) with model deepseek_school

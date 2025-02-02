VERSION = "v2.0.0"
DESCRIPTION = f"域名批量检查工具 {VERSION}"

CLI_HELP_MESSAGE = "显示此帮助信息并退出程序"
CLI_HELP_INPUT = "指定输入文件，默认为 input.txt"
CLI_HELP_OUTPUT = "指定保存过期域名的文件"
CLI_HELP_ERROR = "指定保存未能成功查询的域名的文件"
CLI_HELP_NUM_PROCESSES = "指定并发进程数。未指定则为 1"
CLI_HELP_NUM_THREADS = "指定每进程最大并发线程数。"
CLI_HELP_QUIET = "使程序减少输出。--quiet 或 --quiet True 均可启用此选项"
CLI_HELP_PLUGIN_ID = "指定插件 ID 来进行查询，可用 ID 有（下列 ID 用逗号分隔）：{ids}"

CLI_ERROR_INVAID_PLUGIN_ID = "指定的插件 ID 无效，请使用 --help 参数查询可用插件 ID"
CLI_ERROR_NO_AVAILABLE_PLUGIN = (
    "无可用插件。请正确的在运行目录下放置 plugins 目录，并在其中放置插件文件"
)

INFO_NOT_REGISTER = "❌ {domain}  ⚪ Not Register"
INFO_DATE_NOT_FOUND = "⚠️ {domain}  💻 Date Not Found"
INFO_ERROR_PARSING_DATE = "⚠️ {domain}  💻 Error Parsing Date"
INFO_CHECKING_DATE_EXPIRED = "⚠️ {domain} 💻 Error While Checking Date is Expired"
INFO_EXPIRED = "❌ {domain}  🕐 Expired"
INFO_REDEMPTION_PERIOD = "❌ {domain}  🕐 in Redemption Period"
INFO_NOT_EXPIRED = "✅ {domain}  🆗 Not Expired"
INFO_API_INTERNET_ERROR = "⚠️ {domain}  🛜 API Internet Error"
INFO_API_LIMIT = "⚠️ {domain}  🚫 API Limit"
INFO_API_ERROR = "⚠️ {domain}  🚫 API Error"

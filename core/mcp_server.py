from mcp.server.fastmcp import FastMCP

from chat import run_tool

mcp = FastMCP("school-assistant")


@mcp.tool()
def policy_search(question: str) -> str:
    """Search school policies: timings, fees, leave, sports, transport, contacts."""
    return run_tool("policy_search", {"question": question})


@mcp.tool()
def timetable(class_name: str, day: str = "") -> str:
    """Get a class timetable. class_name like '5'; day like 'Monday' (optional)."""
    return run_tool("timetable", {"class_name": class_name, "day": day})


@mcp.tool()
def results(class_name: str = "", name: str = "", subject: str = "", exam: str = "") -> str:
    """Get exam marks of a student or a class."""
    return run_tool("results", {"class_name": class_name, "name": name,
                                "subject": subject, "exam": exam})


@mcp.tool()
def ranking(class_name: str, exam: str = "Final", top_n: int = 1) -> str:
    """Get the top students of a class by total marks."""
    return run_tool("ranking", {"class_name": class_name, "exam": exam, "top_n": top_n})


@mcp.tool()
def attendance(name: str = "", class_name: str = "") -> str:
    """Get attendance and absences of a student or class."""
    return run_tool("attendance", {"name": name, "class_name": class_name})


if __name__ == "__main__":
    mcp.run()
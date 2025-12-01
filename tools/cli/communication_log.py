#!/usr/bin/env python3
"""
Communication Log System - Development & Automation Tracking
=============================================================

**PURPOSE**: Local logging system for development activities and automation tracking.
**NO EXTERNAL DEPENDENCIES**: Self-contained logging without cloud services.

**Use Cases**:
- Development session logging and milestone tracking
- Automation workflow documentation
- Performance metrics and operation tracking
- Project status reporting

**Output Formats**: JSON, Markdown, and plain text for flexibility.

Comprehensive logging system for automation workflows, development tracking,
and project communication without requiring external service dependencies.
"""

import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class CommunicationLog:
    """
    Advanced communication logging system for AutoFire automation

    Features:
    - Development milestone tracking
    - CLI operation logging
    - Performance metrics
    - Error reporting and resolution tracking
    - Project progress communication
    - Offline operation (no external accounts required)
    """

    def __init__(self, log_dir: str | None = None):
        """Initialize communication log system"""
        self.log_dir = Path(log_dir) if log_dir else Path.cwd() / "communication_logs"
        self.log_dir.mkdir(exist_ok=True)

        # Initialize log files
        self.session_id = f"session_{int(time.time())}"
        self.session_log_file = self.log_dir / f"{self.session_id}.json"
        self.summary_log_file = self.log_dir / "communication_summary.json"

        # Session tracking
        self.session_start = datetime.now()
        self.operations_log = []
        self.milestones_log = []
        self.errors_log = []

        logger.info(f"Communication log initialized: {self.session_log_file}")

    def log_development_milestone(self, milestone: str, details: dict[str, Any]) -> None:
        """Log significant development milestones"""
        milestone_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": "milestone",
            "milestone": milestone,
            "details": details,
            "importance": details.get("importance", "medium"),
        }

        self.milestones_log.append(milestone_entry)
        logger.info(f"📍 Milestone: {milestone}")

        # Write to session log
        self._update_session_log()

    def log_cli_operation(self, operation: str, command: str, result: dict[str, Any]) -> None:
        """Log CLI operations and their results"""
        operation_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": "cli_operation",
            "operation": operation,
            "command": command,
            "result": result,
            "success": result.get("success", True),
            "execution_time": result.get("execution_time", 0),
        }

        self.operations_log.append(operation_entry)
        logger.info(f"🔧 CLI Operation: {operation}")

        # Write to session log
        self._update_session_log()

    def log_error_resolution(self, error: str, resolution: str, context: dict[str, Any]) -> None:
        """Log errors and their resolutions"""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": "error_resolution",
            "error": error,
            "resolution": resolution,
            "context": context,
            "resolved": True,
        }

        self.errors_log.append(error_entry)
        logger.info(f"🔧 Error Resolved: {error}")

        # Write to session log
        self._update_session_log()

    def log_performance_metrics(self, component: str, metrics: dict[str, Any]) -> None:
        """Log performance metrics for components"""
        performance_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": "performance_metrics",
            "component": component,
            "metrics": metrics,
        }

        self.operations_log.append(performance_entry)
        logger.info(f"📊 Performance: {component}")

        # Write to session log
        self._update_session_log()

    def log_project_communication(
        self, message: str, category: str, priority: str = "normal"
    ) -> None:
        """Log project communication messages"""
        comm_entry = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "type": "communication",
            "message": message,
            "category": category,
            "priority": priority,
        }

        self.operations_log.append(comm_entry)
        logger.info(f"💬 Communication [{category}]: {message}")

        # Write to session log
        self._update_session_log()

    def generate_session_summary(self) -> dict[str, Any]:
        """Generate comprehensive session summary"""
        session_duration = datetime.now() - self.session_start

        summary = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.session_start.isoformat(),
                "end_time": datetime.now().isoformat(),
                "duration_seconds": session_duration.total_seconds(),
                "duration_formatted": str(session_duration),
            },
            "statistics": {
                "total_milestones": len(self.milestones_log),
                "total_operations": len(
                    [op for op in self.operations_log if op["type"] == "cli_operation"]
                ),
                "total_communications": len(
                    [op for op in self.operations_log if op["type"] == "communication"]
                ),
                "total_errors_resolved": len(self.errors_log),
                "success_rate": self._calculate_success_rate(),
            },
            "milestones_achieved": [
                {
                    "milestone": m["milestone"],
                    "timestamp": m["timestamp"],
                    "importance": m["details"].get("importance", "medium"),
                }
                for m in self.milestones_log
            ],
            "key_operations": [
                {
                    "operation": op["operation"],
                    "timestamp": op["timestamp"],
                    "success": op["success"],
                }
                for op in self.operations_log
                if op["type"] == "cli_operation"
            ],
            "communication_highlights": [
                {
                    "message": comm["message"],
                    "category": comm["category"],
                    "priority": comm["priority"],
                    "timestamp": comm["timestamp"],
                }
                for comm in self.operations_log
                if comm["type"] == "communication"
            ],
        }

        return summary

    def export_communication_report(self, format_type: str = "markdown") -> str:
        """Export comprehensive communication report"""
        summary = self.generate_session_summary()

        if format_type == "markdown":
            return self._generate_markdown_report(summary)
        elif format_type == "json":
            return json.dumps(summary, indent=2)
        elif format_type == "text":
            return self._generate_text_report(summary)
        else:
            raise ValueError(f"Unsupported format: {format_type}")

    def _generate_markdown_report(self, summary: dict[str, Any]) -> str:
        """Generate markdown communication report"""
        report_lines = [
            "# AutoFire Development Communication Report",
            f"**Session ID:** {summary['session_info']['session_id']}",
            f"**Duration:** {summary['session_info']['duration_formatted']}",
            f"**Generated:** {summary['session_info']['end_time']}",
            "",
            "## 📊 Session Statistics",
            f"- **Milestones Achieved:** {summary['statistics']['total_milestones']}",
            f"- **CLI Operations:** {summary['statistics']['total_operations']}",
            f"- **Communications Logged:** {summary['statistics']['total_communications']}",
            f"- **Errors Resolved:** {summary['statistics']['total_errors_resolved']}",
            f"- **Success Rate:** {summary['statistics']['success_rate']:.1%}",
            "",
            "## 🎯 Key Milestones Achieved",
        ]

        for milestone in summary["milestones_achieved"]:
            importance_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                milestone["importance"], "⚪"
            )
            report_lines.append(
                f"- {importance_emoji} **{milestone['milestone']}** _{milestone['timestamp']}_"
            )

        report_lines.extend(["", "## 🔧 Key Operations Performed"])

        for operation in summary["key_operations"]:
            status_emoji = "✅" if operation["success"] else "❌"
            report_lines.append(
                f"- {status_emoji} **{operation['operation']}** _{operation['timestamp']}_"
            )

        report_lines.extend(["", "## 💬 Communication Highlights"])

        for comm in summary["communication_highlights"]:
            priority_emoji = {"high": "🔴", "normal": "🟡", "low": "🟢"}.get(comm["priority"], "⚪")
            msg = f"**[{comm['category']}]** {comm['message']}"
            report_lines.append(f"- {priority_emoji} {msg} _{comm['timestamp']}_")

        return "\n".join(report_lines)

    def _generate_text_report(self, summary: dict[str, Any]) -> str:
        """Generate plain text communication report"""
        report_lines = [
            "=== AutoFire Development Communication Report ===",
            f"Session ID: {summary['session_info']['session_id']}",
            f"Duration: {summary['session_info']['duration_formatted']}",
            f"Generated: {summary['session_info']['end_time']}",
            "",
            "SESSION STATISTICS:",
            f"  Milestones Achieved: {summary['statistics']['total_milestones']}",
            f"  CLI Operations: {summary['statistics']['total_operations']}",
            f"  Communications Logged: {summary['statistics']['total_communications']}",
            f"  Errors Resolved: {summary['statistics']['total_errors_resolved']}",
            f"  Success Rate: {summary['statistics']['success_rate']:.1%}",
            "",
            "KEY MILESTONES:",
        ]

        for milestone in summary["milestones_achieved"]:
            ms_text = f"{milestone['milestone']} ({milestone['importance']})"
            report_lines.append(f"  - {ms_text} - {milestone['timestamp']}")

        report_lines.extend(["", "KEY OPERATIONS:"])

        for operation in summary["key_operations"]:
            status = "SUCCESS" if operation["success"] else "FAILED"
            report_lines.append(
                f"  - {operation['operation']} ({status}) - {operation['timestamp']}"
            )

        return "\n".join(report_lines)

    def _calculate_success_rate(self) -> float:
        """Calculate operation success rate"""
        cli_operations = [op for op in self.operations_log if op["type"] == "cli_operation"]
        if not cli_operations:
            return 1.0

        successful_ops = sum(1 for op in cli_operations if op["success"])
        return successful_ops / len(cli_operations)

    def _update_session_log(self) -> None:
        """Update session log file"""
        session_data = {
            "session_info": {
                "session_id": self.session_id,
                "start_time": self.session_start.isoformat(),
                "last_updated": datetime.now().isoformat(),
            },
            "milestones": self.milestones_log,
            "operations": self.operations_log,
            "errors": self.errors_log,
        }

        try:
            with open(self.session_log_file, "w") as f:
                json.dump(session_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to update session log: {e}")

    def finalize_session(self) -> str:
        """Finalize session and generate final report"""
        summary = self.generate_session_summary()

        # Update summary log
        try:
            if self.summary_log_file.exists():
                with open(self.summary_log_file) as f:
                    all_summaries = json.load(f)
            else:
                all_summaries = []

            all_summaries.append(summary)

            with open(self.summary_log_file, "w") as f:
                json.dump(all_summaries, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to update summary log: {e}")

        # Generate final report
        report_file = self.log_dir / f"{self.session_id}_report.md"
        markdown_report = self.export_communication_report("markdown")

        try:
            with open(report_file, "w") as f:
                f.write(markdown_report)

            logger.info(f"📋 Final report generated: {report_file}")
            return str(report_file)

        except Exception as e:
            logger.error(f"Failed to generate final report: {e}")
            return markdown_report


def cli_main():
    """CLI interface for communication logging"""
    import argparse

    parser = argparse.ArgumentParser(description="AutoFire Communication Log System")
    parser.add_argument("--log-dir", help="Directory for log files")
    parser.add_argument(
        "--action",
        choices=["milestone", "operation", "error", "communication", "report"],
        required=True,
        help="Action to perform",
    )
    parser.add_argument("--message", help="Message or description")
    parser.add_argument("--category", help="Category for communication")
    parser.add_argument("--priority", choices=["high", "normal", "low"], default="normal")
    parser.add_argument("--format", choices=["markdown", "json", "text"], default="markdown")
    parser.add_argument("--session-id", help="Existing session ID to use")

    args = parser.parse_args()

    # Initialize communication log
    comm_log = CommunicationLog(args.log_dir)

    if args.session_id:
        comm_log.session_id = args.session_id
        comm_log.session_log_file = comm_log.log_dir / f"{args.session_id}.json"

    try:
        if args.action == "milestone":
            if not args.message:
                print("Error: --message required for milestone action")
                return

            details = {"importance": args.priority}
            comm_log.log_development_milestone(args.message, details)
            print(f"✅ Milestone logged: {args.message}")

        elif args.action == "operation":
            if not args.message:
                print("Error: --message required for operation action")
                return

            result = {"success": True, "execution_time": 0.1}
            comm_log.log_cli_operation(args.message, f"manual_{args.message}", result)
            print(f"✅ Operation logged: {args.message}")

        elif args.action == "communication":
            if not args.message or not args.category:
                print("Error: --message and --category required for communication action")
                return

            comm_log.log_project_communication(args.message, args.category, args.priority)
            print(f"✅ Communication logged: {args.message}")

        elif args.action == "report":
            report = comm_log.export_communication_report(args.format)
            print(report)

            # Also save to file
            report_file = comm_log.finalize_session()
            print(f"\n📋 Report saved to: {report_file}")

    except Exception as e:
        print(f"❌ Error: {e}")
        logger.error(f"CLI action failed: {e}")


if __name__ == "__main__":
    cli_main()

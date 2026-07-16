from mobile_ai_system.infrastructure.logging.logger import get_logger
from .base_agent import BaseAgent

logger = get_logger(__name__)


class SupervisorAgent(BaseAgent):

    @property
    def name(self):
        return "Supervisor"

    def run(self, state):

        # =================================================
        # ⚙️ ITERATION CONTROL
        # =================================================

        max_iterations = state.get("max_iterations", 3)
        iteration = state.get("iteration", 0)

        # =================================================
        # 🧠 CROSS-ITERATION MEMORY (NEW CORE)
        # =================================================

        execution_memory = state.setdefault("execution_memory", [])

        logger.info(
            "Iteration %d | Execution memory size: %d",
            iteration,
            len(execution_memory),
        )

        # =================================================
        # 🧠 CURRENT MEMORY INPUTS
        # =================================================

        memory = state.get("memory")
        request = state.get("user_request", "").lower()

        lessons = []
        low_score = 0
        high_score = 0

        if memory is not None:

            for r in memory.latest_reflections(n=10):
                score = r.get("score", 0)
                lessons.append(r.get("lesson", ""))

                if score < 0.7:
                    low_score += 1
                else:
                    high_score += 1

        # =================================================
        # 🧭 STRATEGY SELECTION (NOW MEMORY-AWARE ACROSS ITERATIONS)
        # =================================================

        strategy = self._select_strategy(
            request,
            low_score,
            high_score,
            iteration,
            execution_memory,
        )

        tasks = self._build_tasks(strategy)

        # =================================================
        # 🔁 SELF-CORRECTION INPUT
        # =================================================

        evaluation_score = state.get("evaluation_score")

        should_continue = True

        if evaluation_score is not None:

            logger.info(
                "Iteration %d | Evaluation score: %.2f",
                iteration,
                evaluation_score,
            )

            if evaluation_score >= 0.85:
                should_continue = False

            elif evaluation_score < 0.6:
                should_continue = True
                tasks = [
                    "information_retrieval",
                    "impact_analysis",
                    "report_generation",
                    "evaluation",
                ]

        # =================================================
        # 🧠 UPDATE EXECUTION MEMORY (NEW CORE FEATURE)
        # =================================================

        execution_memory.append(
            {
                "iteration": iteration,
                "strategy": strategy,
                "tasks": tasks,
                "evaluation_score": evaluation_score,
                "lesson_count": len(lessons),
            }
        )

        # =================================================
        # 🧠 CROSS-ITERATION INSIGHT EXTRACTION
        # =================================================

        improving = self._is_improving(execution_memory)

        if improving:
            logger.info("Performance trend improving across iterations")

        else:
            logger.warning("No improvement trend detected")

        # =================================================
        # FINALIZE STATE
        # =================================================

        state["task_list"] = tasks
        state["strategy"] = strategy
        state["iteration"] = iteration + 1
        state["execution_memory"] = execution_memory
        state["active_lessons"] = lessons[:5]
        state["should_continue"] = (
            should_continue and iteration + 1 < max_iterations
        )
        state["improving_trend"] = improving

        return state

    # =================================================
    # 🧩 STRATEGY SELECTOR (NOW CROSS-ITERATION AWARE)
    # =================================================

    def _select_strategy(
        self,
        request,
        low_score,
        high_score,
        iteration,
        execution_memory,
    ):

        # first iteration
        if iteration == 0:

            if low_score > high_score:
                return "deep_analysis"

            return "analysis_path"

        # later iterations → adapt based on trend
        if len(execution_memory) >= 2:

            last = execution_memory[-1]
            prev = execution_memory[-2]

            # improvement detected → simplify
            if (
                last.get("evaluation_score", 0) >
                prev.get("evaluation_score", 0)
            ):
                return "analysis_path"

            # degradation → intensify
            else:
                return "deep_analysis"

        return "analysis_path"

    # =================================================
    # 🧩 TREND ANALYSIS
    # =================================================

    def _is_improving(self, execution_memory):

        if len(execution_memory) < 2:
            return False

        scores = [
            x.get("evaluation_score") or 0
            for x in execution_memory
        ]

        return scores[-1] > scores[0]

    # =================================================
    # 🧩 TASK BUILDER
    # =================================================

    def _build_tasks(self, strategy):

        if strategy == "fast_path":
            return ["information_retrieval"]

        if strategy == "analysis_path":
            return ["information_retrieval", "impact_analysis"]

        if strategy == "deep_analysis":
            return [
                "information_retrieval",
                "impact_analysis",
                "report_generation",
                "evaluation",
            ]

        return ["information_retrieval"]
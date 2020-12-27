package ottop.sudoku;

import ottop.sudoku.puzzle.IPuzzle;

import java.util.*;

/** Container of an array of digits placed in cells, as a solution
 * for the next iteration of the puzzle solver.
 */
public class SolutionContainer {
	private Map<Coord, Integer> sols = new HashMap<Coord, Integer>();;
	private Map<Coord, List<String>> reasons = new HashMap<Coord, List<String>>();
	private IPuzzle myPuzzle;
	private boolean trace;

	public SolutionContainer(IPuzzle p, boolean trace) {
		myPuzzle = p;
		this.trace = trace;
	}

	public void addSolution(Coord c, int n, String reason) {
		if (sols.containsKey(c)) {
			if (sols.get(c) != n) {
				throw new RuntimeException("ERROR: trying to place " + myPuzzle.symbolCodeToSymbol(n) + " at " + c + " which is occupied by " + myPuzzle.symbolCodeToSymbol(sols.get(c)));
			} else {
				if (reason != null) {
					if (reasons.containsKey(c)) {
						reasons.get(c).add(reason);
					} else {
						reasons.put(c, new ArrayList<>(Collections.singleton(reason)));
					}
				}
			}
		} else {
			if (trace) {
				System.out.println("Put " + myPuzzle.symbolCodeToSymbol(n) + " at " + c + " (" + reason + ")");
			}
			sols.put(c, n);
			if (reason != null) {
				reasons.put(c, new ArrayList<>(Collections.singleton(reason)));
			}
		}
	}

	public int size() {
		return sols.keySet().size();
	}

	public Map<Coord, Integer> getSolutions()
	{
		return sols;
	}

	public String toString() {
		StringBuffer result = new StringBuffer();
		boolean isFirst = true;
		result.append("(");
		for (Coord c: sols.keySet()) {
			if (!isFirst) result.append(", ");
			result.append(c).append(":").append(sols.get(c));
			if (reasons.containsKey(c)) {
				result.append(" ").append(reasons.get(c));
			}
			isFirst = false;
		}
		result.append(")");
		return result.toString();
	}
}

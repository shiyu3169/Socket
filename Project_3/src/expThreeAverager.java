import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Created by Ben_Big on 2/25/17.
 */
public class expThreeAverager {
    int numTrials;

    public expThreeAverager(int numTrials){
        this.numTrials=numTrials;
    }

    private HashMap<Double, List<Float>> averagedResult=new HashMap<>();



    public void addResult(HashMap<Double,List<Float>> oneResult){
        for (Map.Entry<Double,List<Float>> entry:oneResult.entrySet()) {
            double time=entry.getKey();
            List<Float> result=entry.getValue();

            if (!averagedResult.containsKey(time)) {
                List<Float> newResult = new ArrayList<>();
                for (int i = 0; i < result.size(); i++) {
                    newResult.add(i, result.get(i) / numTrials);
                }
                averagedResult.put(time, newResult);
            } else {
                List<Float> newResult = new ArrayList<>();
                for (int i = 0; i < result.size(); i++) {
                    newResult.add(i, result.get(i) / numTrials + averagedResult.get(time).get(i));
                }
                averagedResult.replace(time, newResult);
            }
        }
    }

    @Override
    public String toString(){
        return averagedResult.toString();
    }

}

import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/**
 * Created by Ben_Big on 2/23/17.
 */
public class lineObjectAnalyzer {

    HashMap<Integer,Float> sentAt=new HashMap<>();
    int numSentPackets=0;
    int numDroppedPackets=0;
    HashMap<Integer,Boolean> wasDropped=new HashMap<>();
    int dataReceived=0;
    float startTime=-1;
    float time=0;
    ArrayList<Float> RTTs=new ArrayList<>();



    public static boolean findLinesOfInterest(String line){
        Pattern pattern = Pattern.compile("^d .* tcp" +   //Dropped Packet
                "|^r (?:\\S+ ){2}(?<to>\\S+) (?:tcp|ack) (?:\\S+ ){4}(\\k<to>)\\." +   //Packet arrives at destination
                "|^\\- .*? (?<from>\\S+) \\d+ tcp .*? (\\k<from>)\\."); //Packet is sent out from a router
        Matcher m = pattern.matcher(line);
        return m.find();
    }

    protected void processNewLine (lineObject line){
        this.time=line.time;

        if (this.startTime<0){
            this.startTime=line.time;
        }

        if (line.type.equals("tcp")){
            parseTcp(line);
        }

        if (line.type.equals("ack")) {
            parseAck(line);
        }
    }


    protected void parseTcp(lineObject line){
        if (line.event.equals("-")){
            if (line.frm==line.src){
                sentAt.put(line.seq,line.time);
                numSentPackets++;
            }
        }
        else if(line.event.equals("+")){
            return;
        }
        else if(line.event.equals("d")){
            numDroppedPackets++;
            if (sentAt.containsKey(line.seq)) sentAt.remove(line.seq);
            wasDropped.put(line.seq,true);
        }
        else if(line.event.equals("r")){
            if (line.dest==line.to) dataReceived+=line.size;
        }
        else{
         //   throw (new Exception("Unknown event type"));
        }
    }

    protected void parseAck(lineObject line){
        if (line.event.equals("r") && line.dest==line.to){
            HashSet<Integer> toRemove=new HashSet<>();
            for (Map.Entry<Integer,Float> entry : sentAt.entrySet()){
                int sequenceNumber=entry.getKey();
                float sentTime=entry.getValue();
                if (sequenceNumber<line.seq  && !wasDropped.containsKey(sequenceNumber)){
                    float rtt=line.time-sentTime;
                    RTTs.add(rtt);
                    toRemove.add(sequenceNumber);
                }
            }
            for (int packetSeriesNumber : toRemove){
                if (sentAt.containsKey(packetSeriesNumber)){
                    sentAt.remove(packetSeriesNumber);
                }
                if (wasDropped.containsKey(packetSeriesNumber)){
                    wasDropped.remove(packetSeriesNumber);
                }
            }
        }
    }


    public void reset(){
        numSentPackets=0;
        startTime=time;
        RTTs=new ArrayList<>();
        dataReceived=0;
        numDroppedPackets=0;
    }



    public float getDropRate(){
        return (float)numDroppedPackets/(float)numSentPackets;
    }

    public float getAverageRTT(){
        float sumRTT=0;
        for (float t : RTTs) {
            sumRTT+=t;
        }

        return sumRTT/(float)RTTs.size();
    }

    public double getThroughput(){
        /*
        if (startTime<0) {
            throw (new Exception("Flow has not started yet"));
        }*/

        return 0.000008*dataReceived/(time-startTime);
    }
}

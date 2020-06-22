import java.io.*;
import java.nio.charset.Charset;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Properties;

import edu.stanford.nlp.ling.CoreAnnotations.NamedEntityTagAnnotation;
import edu.stanford.nlp.ling.CoreAnnotations.TokensAnnotation;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;

public class Characters {

    //Reads a file to a string and annotates words returning annotated document
    //For example, every word that is a name is marked as "PERSON"
    //Doesn't consider co-references due to low heap memory
    public static Annotation annotate(File file){

        String text = "";
        try {
            text = Files.readString(Paths.get(file.getPath()));
        } catch (IOException e) {
            e.printStackTrace();
        }

        Annotation document = new Annotation(text);

        Properties props = new Properties();

        props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner");

        StanfordCoreNLP pipeline = new StanfordCoreNLP(props);

        pipeline.annotate(document);

        return document;

    }

    //Takes an annotated document and returns a list of characters with their positions in the novel
    public static List<Character> listOfCharacters(Annotation document){

        List<Character> characters = new ArrayList<Character>();
        int tokenCounter = 1;
        String currNeToken = "";

        //Loop through tokens and save every token that is a "PERSON" with its position
        for (CoreLabel token : document.get(TokensAnnotation.class)) {

            currNeToken = token.get(NamedEntityTagAnnotation.class);

            if (currNeToken.equals("PERSON")) {

                String name = token.word().toLowerCase();
                if(token.word().indexOf(',') != -1) {
                    name = name.substring(0, token.word().indexOf(','));
                }
                Character character = new Character(tokenCounter, name);
                characters.add(character);
            }

            tokenCounter++;
        }

        //If there are more consecutive "PERSON" tokens, they represent one name
        //So in those cases concatenate those tokens, delete all tokens except one and change its position
        //to the position of the first token
        for (int i = 0; i < characters.size()-1; i++) {
            if (characters.get(i).getPosition() == (characters.get(i + 1).getPosition() -1)) {
                String fullName = characters.get(i).getName()+ " " + characters.get(i+1).getName();
                characters.get(i+1).setName(fullName);
                characters.get(i).setDelete(true);
            }
        }

        for (int i = 0; i < characters.size()-1; i++) {
            if (characters.get(i).isDelete()){
                characters.remove(characters.get(i));
                i--;
            } else if (characters.get(i).getName().split(" ").length > 1) {
                characters.get(i).setPosition(characters.get(i).getPosition()-characters.get(i).getName().split(" ").length+1);
            }
        }

        return characters;
    }

    //Writes list of character names and positions into a csv file
    public static void writeToFile(List<Character> characters, String filename){

        OutputStreamWriter writer;
        try {
            writer = new OutputStreamWriter(
                    new FileOutputStream("../indexes_2/" + filename + ".csv"),
                    Charset.forName("UTF-8").newEncoder()
            );
            for (Character character : characters) {

                writer.write(character.toString() +"\n");

            }

            writer.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public static void main(String[] args) {

        File folder = new File("../books_2");

        File[] listOfFiles = folder.listFiles();
        if(listOfFiles == null){
            return;
        }

        //Loop through all books in folder books, annotate them, find all characters and save them in indexes folder
        for (int j = 0; j < listOfFiles.length; j++) {

            if (listOfFiles[j].getName().endsWith(".txt")) {
                File file = listOfFiles[j];
                System.out.println(file.getName());
                Annotation document = annotate(file);
                List<Character> characters = listOfCharacters(document);
                writeToFile(characters, file.getName().substring(0, file.getName().lastIndexOf('.')));
            }

        }


    }
}

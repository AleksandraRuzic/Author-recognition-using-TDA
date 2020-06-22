//This class represents one appearance of a character in a novel
//Has attributes: character name, position in the novel and an indicator showing if it should be deleted because its
//a part of a name with more words
public class Character {

    private int position;
    private String name;
    private boolean delete;

    Character(int position, String name){
        this.position = position;
        this.name = name;
        this.delete = false;
    }

    public int getPosition() {
        return position;
    }

    public void setPosition(int position) {
        this.position = position;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public boolean isDelete() {
        return delete;
    }

    public void setDelete(boolean delete) {
        this.delete = delete;
    }

    @Override
    public String toString() {
        return this.position + "," + this.name;
    }
}

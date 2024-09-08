import sqlite3
import tkinter as tk
from tkinter import ttk

# List of specializations for wizards
wizard_specializations = [
    'All', 'Abjuration', 'Alteration', 'Conjuration/Summoning', 
    'Divination', 'Enchantment/Charm', 'Illusion/Phantasm', 
    'Invocation/Evocation', 'Necromancy', 'Elemental Air', 
    'Elemental Earth', 'Elemental Fire', 'Elemental Water', 
    'Dimension', 'Force', 'Mentalism', 'Shadow', 'Alchemy', 
    'Artifice', 'Geometry', 'Song', 'Wild Magic', 'Wizard Only'
]

# List of deities for priests
deities = [
    'Astair', 'Felumbra', 'Nadinis', 'Martha', 'Voraci', 'Malkis', 'Tempos',
    'Mathis / Safia', 'Efra', 'Nerual', 'Quantarius', 'Terrin', 'Chis', 
    'Jexel', 'Reluna', 'Agepa', 'Bellum', 'Sayor', 'Solt', 'Velmontarious', 
    'Velthara', 'Womaatoar', 'Aaris', 'Matrigal', 'Ponos', 'Terrasa', 'Illumis', 'Relkor'
]


def get_spells_for_specialization(specialization):
    #may need to change based on file path
    conn = sqlite3.connect('2e_spells.db')
    cursor = conn.cursor()

    # If "All" is selected, return all mage spells
    if specialization == 'All':
        query = '''
        SELECT DISTINCT s.id, s.spell_name, s.level
        FROM Spells s
        WHERE s.class = 'wizard'
        ORDER BY s.level, s.spell_name;
        '''
        cursor.execute(query)

    elif specialization == 'Wizard Only':
        query = '''
        SELECT DISTINCT s.id, s.spell_name, s.level
        FROM Spells s
        WHERE s.class = 'wizard'
        ORDER BY s.level, s.spell_name;
        '''
        cursor.execute(query)

    else:
        query = '''
        SELECT DISTINCT s.id, s.spell_name, s.level
        FROM Spells s
        JOIN Spell_Specializations ss ON s.id = ss.spell_id
        JOIN Specializations sp ON ss.specialization_id = sp.id
        WHERE sp.specialization_name = ?
        AND s.class = 'wizard'

        UNION

        SELECT DISTINCT s.id, s.spell_name, s.level
        FROM Spells s
        WHERE s.school NOT IN (
            SELECT opposed_specialization_name 
            FROM Opposed_Specializations 
            WHERE specialization_name = ?
        )
        AND s.class = 'wizard'

        ORDER BY s.level, s.spell_name;
        '''
        cursor.execute(query, (specialization, specialization))

    results = cursor.fetchall()
    conn.close()
    return results

# Function to check if a spell is part of the selected specialization
def is_specialization_spell(spell_id, specialization):
    # Skip checking for "All" and "Wizard Only"
    if specialization in ['All', 'Wizard Only']:
        return False

    conn = sqlite3.connect('2e_spells.db')
    cursor = conn.cursor()

    query = '''
    SELECT 1 FROM Spell_Specializations ss
    JOIN Specializations sp ON ss.specialization_id = sp.id
    WHERE ss.spell_id = ? AND sp.specialization_name = ?
    '''
    cursor.execute(query, (spell_id, specialization))
    result = cursor.fetchone()

    conn.close()
    return result is not None

# Function to get priest spells based on deity
def get_priest_spells_for_deity(deity):

    conn = sqlite3.connect('2e_spells.db')
    cursor = conn.cursor()


    query = '''
    SELECT DISTINCT s.spell_name, s.level, sp.sphere_name
    FROM Spells s
    JOIN Spell_Spheres ss ON s.id = ss.spell_id
    JOIN Spheres sp ON ss.sphere_id = sp.id
    JOIN Deity_Sphere_Access dsa ON sp.sphere_name = dsa.sphere
    JOIN Deities d ON d.deity_name = dsa.deity
    WHERE d.deity_name = ?
    AND (
        (dsa.access_level = 'Major') OR
        (dsa.access_level = 'Minor' AND s.level <= 3)
    )
    ORDER BY s.level, s.spell_name;
    '''

    cursor.execute(query, (deity,))
    results = cursor.fetchall()
    conn.close()
    return results

# Function to display spells in the text box
def show_spells():

    text_box.delete(1.0, tk.END)

    # Check if wizard or priest dropdown is selected
    if combo.get() != 'None':
        specialization = combo.get()
        spells = get_spells_for_specialization(specialization)

        if spells:
            for spell in spells:
                spell_id = spell[0]
                spell_text = f"ID: {spell_id}, Spell: {spell[1]}, Level: {spell[2]}\n"
                
                # Highlight if the spell is part of the specialization
                if is_specialization_spell(spell_id, specialization):
                    text_box.insert(tk.END, spell_text, 'highlight')  # Highlight tag
                else:
                    text_box.insert(tk.END, spell_text)
        else:
            text_box.insert(tk.END, f"No wizard spells found for '{specialization}'.")

    elif deity_combo.get() != 'None':
        deity = deity_combo.get()
        priest_spells = get_priest_spells_for_deity(deity)

        if priest_spells:
            for spell in priest_spells:
                text_box.insert(tk.END, f"Spell: {spell[0]}, Level: {spell[1]}, Sphere: {spell[2]}\n")
        else:
            text_box.insert(tk.END, f"No priest spells found for deity '{deity}'.")


root = tk.Tk()
root.title("Mage and Priest Spell Finder")

# Create a label for wizard specialization dropdown
wizard_label = tk.Label(root, text="Select a Wizard Specialization:")
wizard_label.pack(pady=10)

# Create a dropdown menu (combobox) for wizard specializations
combo = ttk.Combobox(root, values=wizard_specializations, state="readonly")
combo.pack(pady=10)
combo.set('None')

# Create a label for priest deity dropdown
priest_label = tk.Label(root, text="Select a Priest Deity:")
priest_label.pack(pady=10)

# Create a dropdown menu (combobox) for priest deities
deity_combo = ttk.Combobox(root, values=deities, state="readonly")
deity_combo.pack(pady=10)
deity_combo.set('None')


button = tk.Button(root, text="Show Spells", command=show_spells)
button.pack(pady=10)

text_box = tk.Text(root, height=20, width=80)
text_box.pack(pady=10)

text_box.tag_config('highlight', background='yellow', foreground='black')

root.mainloop()
